import logging
from datetime import timedelta, datetime

import pytz
from django.contrib.auth import login, get_user_model, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic

from GuideToExile.models import BuildGuide, UserProfile, GuideComment, GuideLike, ActiveSkill
from . import skill_tree, build_guide, items_service, guide_search
from .forms import SignUpForm, PobStringForm, EditGuideForm, ProfileForm, GuideListFilterForm, URL_REGEX, \
    UserDeleteForm
from .settings import LIKES_RECENTLY_OFFSET
from .tokens import account_activation_token

logger = logging.getLogger('guidetoexile')

skill_tree_service = skill_tree.SkillTreeService()

GEAR_SLOTS = ['weapon-1', 'weapon-2', 'helmet', 'body-armour', 'belt', 'ring-1', 'ring-2', 'amulet', 'boots', 'gloves',
              'flask-1', 'flask-2', 'flask-3', 'flask-4', 'flask-5']


class LikedGuidesView(generic.ListView):
    template_name = 'liked_guides.html'
    paginate_by = 50

    def get_queryset(self):
        return BuildGuide.objects.defer('pob_details', 'pob_string', 'text').filter(guidelike__is_active=True,
                                                                                    guidelike__user=self.request.user.userprofile).all()


def index_view(request):
    form = GuideListFilterForm(initial=request.GET)
    if not request.user.is_authenticated:
        form.fields['liked_by_me'].disabled = True
    return render(request, 'index.html', {
        'titles': BuildGuide.objects.values('title').distinct(),
        'authors': BuildGuide.objects.values('author__user__username').distinct(),
        'filter_form': form,
    })


def guide_list_view(request):
    paginate_by = 50
    form = GuideListFilterForm(request.GET)
    if form.is_valid():
        user_id = request.user.userprofile.user_id if request.user.is_authenticated else 0
        page = request.GET.get('page')
        page_obj = guide_search.find_with_filter(form, user_id, page, paginate_by)
        return render(request, 'guide_list.html', {'page_obj': page_obj})


def show_guide_view(request, pk, slug):
    logger.info('Show guide pk=%s', pk)
    guide = get_object_or_404(BuildGuide, guide_id=pk)

    return render(request, 'show_guide.html',
                  {'pk': pk, 'build_guide': guide})


def show_draft_view(request, pk):
    guide = get_object_or_404(BuildGuide, guide_id=pk)
    if request.user.userprofile != guide.author:
        return HttpResponseForbidden
    draft = guide if guide.status == BuildGuide.GuideStatus.DRAFT else guide.draft

    return render(request, 'show_guide.html',
                  {'pk': draft.guide_id, 'build_guide': draft})


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


class MyGuidesListView(generic.ListView):
    template_name = 'guide_list.html'
    paginate_by = 50

    def get_queryset(self):
        return guide_search.find_all_by_user(self.request.user.userprofile)


def my_guides_view(request):
    return render(request, 'my_guides.html')


def authors_view(request):
    return render(request, 'authors.html')


def authors_list_view(request):
    recently_threshold = datetime.today() - timedelta(days=LIKES_RECENTLY_OFFSET)
    is_public_q = Q(buildguide__status=BuildGuide.GuideStatus.PUBLIC)
    is_active_q = Q(buildguide__guidelike__is_active=True)
    recently_q = Q(
        buildguide__guidelike__creation_datetime__gte=recently_threshold)
    authors = (UserProfile.objects.filter(buildguide__isnull=False, buildguide__status=BuildGuide.GuideStatus.PUBLIC)
               .annotate(likes=Count('buildguide__guidelike', filter=is_active_q & is_public_q))
               .annotate(likes_recently=Count('buildguide__guidelike', filter=is_active_q & recently_q & is_public_q))
               .order_by('-likes', 'user__username'))
    logger.info(authors.query)
    paginate_by = 50
    page = request.GET.get('page')
    paginator = Paginator(authors, paginate_by)
    authors_page = paginator.get_page(page)
    for author in authors_page:
        top3_guides = (BuildGuide.objects
                           .defer('pob_details', 'pob_string', 'text')
                           .filter(author=author.pk)
                           .filter(status=BuildGuide.GuideStatus.PUBLIC)
                           .annotate(likes=Count('guidelike', filter=Q(guidelike__is_active=True)))
                           .order_by('-likes')[:3])
        top3_guides_recently = (BuildGuide.objects
                                    .defer('pob_details', 'pob_string', 'text')
                                    .filter(author=author.pk)
                                    .filter(status=BuildGuide.GuideStatus.PUBLIC)
                                    .annotate(likes_recently=
                                              Count('guidelike',
                                                    filter=Q(guidelike__is_active=True)
                                                           & Q(guidelike__creation_datetime__gte=recently_threshold)))
                                    .order_by('-likes_recently')[:3])
        author.top3_guides = top3_guides
        author.top3_guides_recently = top3_guides_recently

    return render(request, 'authors_list.html', {'page_obj': authors_page})


def new_guide_pob_view(request):
    if request.method == 'POST':
        logger.info('Creating new guide')
        form = PobStringForm(request.POST)
        if form.is_valid():
            build_details, pob_string = form.cleaned_data['pob_input']
            author = request.user.userprofile
            new_build_guide = build_guide.create_build_guide(author, build_details, pob_string, skill_tree_service)
            new_build_guide.save()
            return redirect('edit_guide', pk=new_build_guide.guide_id)

    else:
        form = PobStringForm()

    return render(request, 'pob_string_form.html', {'form': form})


def edit_pob_view(request, pk):
    if request.method == 'POST':
        form = PobStringForm(request.POST)
        if form.is_valid():
            build_details, pob_string = form.cleaned_data['pob_input']
            guide = BuildGuide.objects.get(guide_id=pk)
            build_guide.assign_pob_details_to_guide(guide, build_details, pob_string, skill_tree_service)
            return redirect('edit_guide', pk=guide.guide_id)

    else:
        form = PobStringForm()
    return render(request, 'pob_string_form.html', {'pk': pk, 'form': form})


def publish_guide_view(request, pk):
    draft = BuildGuide.objects.get(guide_id=pk)

    if request.user.userprofile != draft.author:
        return HttpResponseForbidden

    if draft.status != BuildGuide.GuideStatus.DRAFT:
        return HttpResponseForbidden

    public_guide = build_guide.publish_guide(draft)
    return redirect('show_guide', pk=public_guide.guide_id, slug=public_guide.slug)


def archive_guide_view(request, pk):
    guide = BuildGuide.objects.get(guide_id=pk)
    if request.user.userprofile != guide.author:
        return HttpResponseForbidden

    if guide.status == BuildGuide.GuideStatus.DRAFT:
        return HttpResponseForbidden
    guide.status = BuildGuide.GuideStatus.ARCHIVED
    guide.save()
    return redirect('show_guide', pk=guide.guide_id, slug=guide.slug)


def unarchive_guide_view(request, pk):
    guide = BuildGuide.objects.get(guide_id=pk)
    if request.user.userprofile != guide.author:
        return HttpResponseForbidden

    if guide.status == BuildGuide.GuideStatus.DRAFT:
        return HttpResponseForbidden
    guide.status = BuildGuide.GuideStatus.PUBLIC
    guide.save()
    return redirect('show_guide', pk=guide.guide_id, slug=guide.slug)


def clear_draft_view(request, pk):
    guide = BuildGuide.objects.get(guide_id=pk)
    if request.user.userprofile != guide.author:
        return HttpResponseForbidden

    try:
        guide = build_guide.clear_draft(guide.public_version)
        return redirect('show_guide', pk=guide.guide_id, slug=guide.slug)
    except BuildGuide.DoesNotExist:
        guide.delete()
        return redirect('/')


def edit_guide_view(request, pk):
    guide = BuildGuide.objects.get(guide_id=pk)
    if request.user.userprofile != guide.author:
        return HttpResponseForbidden
    draft_guide = guide if guide.status == BuildGuide.GuideStatus.DRAFT else guide.draft
    # Form field requires (value, label) tuples for options, list of those is created here
    active_skills = set((gem.name, gem.name) for skill_group in draft_guide.pob_details.skill_groups
                        for gem in skill_group.gems
                        if gem.is_active_skill and not skill_group.is_ignored)
    active_skills = list(active_skills)
    imported_primary_skill = draft_guide.pob_details.imported_primary_skill
    active_skills.sort(key=lambda v: v[0] == imported_primary_skill, reverse=True)

    if request.method == 'POST':
        logger.info('Editing guide pk=%s', pk)
        data = request.POST.copy()
        if 'primary_skills' not in data:
            data['primary_skills'] = imported_primary_skill
        form = EditGuideForm(active_skills, data)
        if form.is_valid():
            draft_guide.title = form.cleaned_data['title']
            draft_guide.text = form.cleaned_data['text']

            primary_skills_names = form.cleaned_data['primary_skills']
            draft_guide.video_url = form.cleaned_data['video_url']
            if imported_primary_skill not in primary_skills_names:
                primary_skills_names.insert(0, imported_primary_skill)
            draft_guide.pob_details.main_active_skills = primary_skills_names
            draft_guide.primary_skills.clear()
            draft_guide.primary_skills.add(*ActiveSkill.objects.filter(name__in=primary_skills_names).all())

            now = timezone.now()
            draft_guide.modification_datetime = now
            if not draft_guide.creation_datetime:
                draft_guide.creation_datetime = now

            draft_guide.save()

            return redirect('show_draft', pk=pk)

    else:
        form = EditGuideForm(active_skills, initial={'title': draft_guide.title,
                                                     'text': draft_guide.text,
                                                     'video_url': draft_guide.video_url,
                                                     'primary_skills': draft_guide.pob_details.main_active_skills})
    return render(request, 'edit_guide.html', {'form': form, 'pk': pk, 'guide': draft_guide})


def cancel_edit_view(request, pk):
    guide = BuildGuide.objects.get(guide_id=pk)
    if request.user.userprofile != guide.author:
        return HttpResponseForbidden
    if not guide.creation_datetime:
        guide.delete()
        return redirect('/')
    try:
        return redirect('show_guide', pk=guide.public_version.pk, slug=guide.public_version.slug)
    except BuildGuide.DoesNotExist:
        return redirect('show_guide', pk=guide.pk, slug=guide.slug)


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
    guide = BuildGuide.objects.get(guide_id=pk)
    if request.user == guide.author.user:
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
    guide = BuildGuide.objects.get(guide_id=pk)
    if request.user == guide.author.user:
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
    guide = BuildGuide.objects.get(pk=guide_id)
    guide_author_username = guide.author.user.username if guide.author else ''
    return render(request, 'comments.html', {'page_obj': page_obj, 'guide_author_username': guide_author_username})


def add_comment(request, guide_id):
    if not request.user.is_authenticated:
        return HttpResponseForbidden()
    if request.method == 'POST':
        comment_text = request.POST['comment']
        comment_text = URL_REGEX.sub('[REDACTED LINK]', comment_text)

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
            subject = '[Guide to Exile] Account activation'
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
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
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


class CookiePolicy(generic.TemplateView):
    template_name = "policies/cookies_policy.html"


class PrivacyPolicy(generic.TemplateView):
    template_name = "policies/privacy_policy.html"


class TermsOfUse(generic.TemplateView):
    template_name = "policies/terms_of_use.html"


def delete_user_view(request):
    user = request.user
    if request.method == 'GET':
        form = UserDeleteForm(user=user)
        return render(request, 'registration/user_deletion.html', {'form': form})
    form = UserDeleteForm(request.POST, user=user)
    if form.is_valid():
        logout(request)
        user.delete()
        return redirect('index')
    return render(request, 'registration/user_deletion.html', {'form': form})
