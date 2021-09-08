import logging

import pytz
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic

from GuideToExile.models import BuildGuide, UserProfile, GuideComment, GuideLike, ActiveSkill
from . import skill_tree, build_guide, items_service
from .forms import SignUpForm, NewGuideForm, EditGuideForm, ProfileForm, GuideListFilterForm
from .tokens import account_activation_token

logger = logging.getLogger('guidetoexile')

skill_tree_service = skill_tree.SkillTreeService()

GEAR_SLOTS = ['weapon-1', 'weapon-2', 'helmet', 'body-armour', 'belt', 'ring-1', 'ring-2', 'amulet', 'boots', 'gloves',
              'flask-1', 'flask-2', 'flask-3', 'flask-4', 'flask-5']


class LikedGuidesView(generic.ListView):
    template_name = 'liked_guides.html'
    paginate_by = 50

    def get_queryset(self):
        return BuildGuide.objects.defer('pob_details').filter(guidelike__is_active=True,
                                                              guidelike__user=self.request.user.userprofile).all()


class UserProfileView(generic.DetailView):
    template_name = 'user_profile.html'
    context_object_name = 'user_profile'
    model = UserProfile
    slug_field = 'user_id'
    slug_url_kwarg = 'user_id'
    paginate_by = 50

    def get_context_data(self, **kwargs):
        context = super(UserProfileView, self).get_context_data(**kwargs)
        guides = self.get_related_guides()
        context['guides'] = guides
        context['page_obj'] = guides
        return context

    def get_related_guides(self):
        queryset = self.object.buildguide_set.defer('pob_details').all()
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page')
        return paginator.get_page(page)


def index_view(request):
    form = GuideListFilterForm()
    if not request.user.is_authenticated:
        form.fields['liked_by_me'].disabled = True
    return render(request, 'index.html', {
        'titles': BuildGuide.objects.values('title').distinct(),
        'authors': BuildGuide.objects.values('author__user__username').distinct(),
        'filter_form': form,
    })


def guide_list_view(request):
    paginate_by = 5
    if request.method == 'POST':
        form = GuideListFilterForm(request.POST)
        if form.is_valid():
            user_id = request.user.userprofile.user_id if request.user.is_authenticated else 0
            queryset = BuildGuide.objects.defer('pob_details')
            queryset = queryset.filter(*form.get_filter(user_id))

            queryset = queryset.order_by('creation_datetime').reverse().all()
            logger.debug('Search query=%s', queryset.query)
            paginator = Paginator(queryset, paginate_by)
            page = request.POST.get('page')
            page_obj = paginator.get_page(page)
            return render(request, 'guide_list.html', {'page_obj': page_obj})

    queryset = BuildGuide.objects.defer('pob_details').all()
    paginator = Paginator(queryset, paginate_by)
    page = request.POST.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'guide_list.html', {'page_obj': page_obj})


def show_guide_view(request, pk, slug):
    logger.info('Show guide pk=%s', pk)
    guide = get_object_or_404(BuildGuide, guide_id=pk)

    return render(request, 'show_guide.html',
                  {'pk': pk, 'build_guide': guide})


def guide_tab_view(request, pk):
    guide = get_object_or_404(BuildGuide, guide_id=pk)
    return render(request, 'guide_tab.html', {'pk': pk, 'build_guide': guide})


def gear_gems_tab_view(request, pk):
    guide = get_object_or_404(BuildGuide, guide_id=pk)
    item_sets_with_skills = items_service.assign_skills_to_items(guide.pob_details.item_sets,
                                                                 guide.pob_details.skill_groups)
    return render(request, 'gear_gems_tab.html', {'pk': pk, 'build_guide': guide, 'item_sets': item_sets_with_skills,
                                                  'gear_slots': GEAR_SLOTS})


def skill_tree_tab_view(request, pk):
    guide = get_object_or_404(BuildGuide, guide_id=pk)
    tree_specs = guide.pob_details.tree_specs
    trees = {}
    for tree_spec in tree_specs:
        tree_html = skill_tree_service.get_html_with_taken_nodes(tree_spec.nodes, tree_spec.tree_version)
        keystones = skill_tree_service.get_keystones(tree_spec.nodes, tree_spec.tree_version)
        trees[tree_spec.title] = (tree_html, keystones, tree_spec.url)
    return render(request, 'skill_tree_tab.html', {'pk': pk, 'build_guide': guide, 'trees': trees})


def new_guide_view(request):
    if request.method == 'POST':
        logger.info('Creating new guide')
        form = NewGuideForm(request.POST)
        if form.is_valid():
            build_details, pob_string = form.cleaned_data['pob_input']
            author = request.user.userprofile
            new_build_guide = build_guide.create_build_guide(author, build_details, pob_string, skill_tree_service)
            new_build_guide.save()
            return redirect('edit_guide', pk=new_build_guide.guide_id)

    else:
        form = NewGuideForm()

    return render(request, 'new_guide.html', {'form': form})


def edit_guide_view(request, pk):
    guide = BuildGuide.objects.get(guide_id=pk)
    # Form field requires (value, label) tuples for options, list of those is created here
    active_skills = set((gem.name, gem.name) for skill_group in guide.pob_details.skill_groups
                        for gem in skill_group.gems
                        if gem.is_active_skill)
    active_skills = list(active_skills)
    imported_primary_skill = guide.pob_details.imported_primary_skill
    active_skills.sort(key=lambda v: v[0] == imported_primary_skill, reverse=True)

    if request.method == 'POST':
        logger.info('Editing guide pk=%s', pk)
        data = request.POST.copy()
        if 'primary_skills' not in data:
            data['primary_skills'] = imported_primary_skill
        form = EditGuideForm(active_skills, data)
        if form.is_valid():
            if not guide.creation_datetime:
                guide.creation_datetime = timezone.now()
            guide.modification_datetime = timezone.now()
            guide.title = form.cleaned_data['title']
            guide.text = form.cleaned_data['text']

            primary_skills_names = form.cleaned_data['primary_skills']
            if imported_primary_skill not in primary_skills_names:
                primary_skills_names.insert(0, imported_primary_skill)
            guide.pob_details.main_active_skills = primary_skills_names
            guide.primary_skills.clear()
            guide.primary_skills.add(*ActiveSkill.objects.filter(name__in=primary_skills_names).all())

            guide.save()

            return redirect('show_guide', pk=guide.guide_id, slug=guide.slug)

    else:
        form = EditGuideForm(active_skills, {'title': guide.title,
                                             'text': guide.text,
                                             'primary_skills': guide.pob_details.main_active_skills}, )
    return render(request, 'edit_guide.html', {'form': form, 'pk': pk, 'guide': guide})


def user_settings_view(request):
    user_profile = request.user.userprofile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            if form.cleaned_data['avatar']:
                user_profile.avatar = form.cleaned_data['avatar']
            user_profile.twitch_url = form.cleaned_data['twitch_url']
            user_profile.youtube_url = form.cleaned_data['youtube_url']

            # storing timezone both in DB and session, taking from session first
            user_profile.timezone = request.POST['timezone']
            request.session['django_timezone'] = request.POST['timezone']

            user_profile.save()
            return redirect('/', username=request.user.username)
    else:
        form = ProfileForm(initial={'avatar': user_profile.avatar,
                                    'youtube_url': user_profile.youtube_url,
                                    'twitch_url': user_profile.twitch_url})
    return render(request, 'user_settings.html',
                  {'avatar': user_profile.avatar, 'form': form, 'timezones': pytz.common_timezones})


def guide_likes(request, pk):
    if request.user.is_authenticated:
        do_user_like = GuideLike.objects.filter(user__user=request.user, guide__guide_id=pk, is_active=True).exists()
    else:
        do_user_like = False
    return JsonResponse({'likes_amount': GuideLike.objects.filter(guide__guide_id=pk,
                                                                  is_active=True).count(),
                         'do_user_like': do_user_like})


def add_guide_like(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseForbidden
    if request.method == 'POST':
        guide_like = GuideLike.objects.filter(user__user=request.user, guide__guide_id=pk).first()
        if not guide_like:
            guide_like = GuideLike(user=request.user.userprofile, guide_id=pk)
            guide_like.save()
        elif not guide_like.is_active:
            guide_like.is_active = True
            guide_like.save()
        return HttpResponse(status=200)


def remove_guide_like(request, pk):
    if not request.user.is_authenticated:
        return HttpResponseForbidden
    if request.method == 'POST':
        guide_like = GuideLike.objects.filter(user__user=request.user, guide__guide_id=pk).first()
        if guide_like and guide_like.is_active:
            guide_like.is_active = False
            guide_like.save()
        return HttpResponse(status=200)


def show_comments(request, guide_id):
    paginate_by = 50
    comments_query = GuideComment.objects.filter(guide__guide_id=guide_id).order_by(
        'creation_datetime').reverse().all()
    paginator = Paginator(comments_query, paginate_by)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    return render(request, 'comments.html', {'page_obj': page_obj})


def add_comment(request, guide_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method == 'POST':
        comment_text = request.POST['comment']
        comment = GuideComment()
        comment.author = request.user.userprofile
        comment.guide = get_object_or_404(BuildGuide, guide_id=guide_id)
        comment.creation_datetime = timezone.now()
        comment.text = comment_text
        comment.modification_datetime = timezone.now()
        comment.save()

        return HttpResponse(status=201)


def edit_comment(request):
    if request.method == 'POST':
        comment_id = request.POST['comment_id']
        comment = get_object_or_404(GuideComment, pk=comment_id)
        if comment.author != request.user.userprofile:
            return HttpResponseForbidden()
        comment.text = request.POST['comment']
        comment.modification_datetime = timezone.now()
        comment.save()
        return HttpResponse(status=204)


def delete_comment(request):
    if request.method == 'POST':
        comment_id = request.POST['comment_id']
        comment = get_object_or_404(GuideComment, pk=comment_id)
        if comment.author != request.user.userprofile:
            return HttpResponseForbidden()
        comment.delete()
        return HttpResponse(status=200)


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.userprofile.email = form.cleaned_data.get('email')
            # user can't login until link confirmed
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            # load a template like get_template()
            # and calls its render() method immediately.
            message = render_to_string('registration/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                # method will generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            user.email_user(subject, message)
            return redirect('activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    # checking if the user exists, if the token is valid.
    if user is not None and account_activation_token.check_token(user, token):
        # if valid set active true
        user.is_active = True
        # set signup_confirmation true
        user.userprofile.signup_confirmation = True
        user.save()
        login(request, user)
        return redirect('index')
    else:
        return render(request, 'registration/activation_invalid.html')


def activation_sent_view(request):
    return render(request, 'registration/activation_sent.html')
