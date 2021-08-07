from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
# Create your views here.
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import generic

from BuildsOfExile.models import BuildGuide
from . import skill_tree, build_guide
from .forms import SignUpForm, NewGuideForm, EditGuideForm
from .tokens import account_activation_token

skill_tree_service = skill_tree.SkillTreeService()


class IndexView(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'build_guide_list'
    paginate_by = 100

    def get_queryset(self):
        """Return the last five published questions."""
        return BuildGuide.objects.all()


def show_guide_view(request, pk):
    guide = get_object_or_404(BuildGuide, build_id=pk)
    tree_specs = guide.pob_details['tree_specs']
    tree_graphs = {}
    for tree_spec in tree_specs:
        title = tree_spec['title'] if tree_spec['title'] else 'Default'
        tree_graphs[title] = skill_tree_service.get_html_with_taken_nodes(tree_spec['nodes'], tree_spec['tree_version'])
    return render(request, 'show_guide.html', {'pk': pk, 'build_guide': guide, 'tree_graphs': tree_graphs})


def new_guide_view(request):
    if request.method == 'POST':
        form = NewGuideForm(request.POST)
        if form.is_valid():
            build_details, pob_string = form.cleaned_data['pob_input']
            author = request.user.userprofile
            new_build_guide = build_guide.create_build_guide(author, build_details, pob_string, skill_tree_service)
            new_build_guide.save()
            return redirect('edit_guide', pk=new_build_guide.build_id)

    else:
        form = NewGuideForm()

    return render(request, 'new_guide.html', {'form': form})


def edit_guide_view(request, pk):
    guide = BuildGuide.objects.get(build_id=pk)
    if request.method == 'POST':
        form = EditGuideForm(request.POST)
        if form.is_valid():
            guide.title = form.cleaned_data['title']
            guide.text = form.cleaned_data['text']
            guide.save()
            return redirect('show_guide', pk=guide.build_id)

    else:
        form = EditGuideForm({'title': guide.title,
                              'text': guide.text})

    return render(request, 'edit_guide.html', {'form': form, 'pk': pk, 'guide': guide})


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
