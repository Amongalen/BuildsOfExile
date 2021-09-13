import logging
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.paginator import Paginator, Page
from django.db.models import Q, Count, QuerySet

from GuideToExile.forms import GuideListFilterForm
from GuideToExile.models import BuildGuide
from GuideToExile.settings import LIKES_RECENTLY_OFFSET

logger = logging.getLogger('guidetoexile')


def find_with_filter(filter_form: GuideListFilterForm, user_id: int, page: int, paginate_by: int) -> Page:
    queryset = BuildGuide.objects.defer('pob_details')
    queryset = _annotate_like_counts(queryset)
    base_filters = _get_base_filters(filter_form, user_id)
    queryset = queryset.filter(*base_filters)
    queryset = _filter_keystones(queryset, filter_form)
    queryset = _filter_unique_items(queryset, filter_form)
    queryset = _apply_order(queryset, filter_form)
    queryset = queryset.all()
    logger.debug('Search query=%s', queryset.query)
    page_obj = _get_page(page, paginate_by, queryset)
    return page_obj


def find_all(page: int, paginate_by: int) -> Page:
    queryset = BuildGuide.objects.defer('pob_details')
    queryset = _annotate_like_counts(queryset)
    queryset = queryset.order_by('likes').all()
    return _get_page(page, paginate_by, queryset)


def find_all_by_user(user: User) -> QuerySet:
    queryset = BuildGuide.objects.defer('pob_details')
    queryset = _annotate_like_counts(queryset)
    queryset = queryset.filter(author__user=user)
    queryset = queryset.order_by('-modification_datetime').all()
    return queryset


def _annotate_like_counts(queryset: QuerySet) -> QuerySet:
    recently_threshold = datetime.today() - timedelta(days=LIKES_RECENTLY_OFFSET)
    return queryset.annotate(
        likes=Count('guidelike', filter=Q(guidelike__is_active=True))).annotate(
        likes_recently=Count('guidelike', filter=Q(guidelike__is_active=True) & Q(
            guidelike__creation_datetime__gte=recently_threshold)))


def _get_page(page: int, paginate_by: int, queryset: QuerySet) -> Page:
    paginator = Paginator(queryset, paginate_by)
    page_obj = paginator.get_page(page)
    return page_obj


def _filter_keystones(queryset: QuerySet, filter_form: GuideListFilterForm) -> QuerySet:
    keystone_keys = filter_form.cleaned_data['keystones']
    if keystone_keys:
        keystone_choices = dict(filter_form.fields['keystones'].choices)
        keystones = [keystone_choices[int(keystone_key)] for keystone_key in keystone_keys]
        queryset = queryset.filter(keystones__name__in=keystones)
        queryset = queryset.annotate(num_keystones=Count('keystones'))
        queryset = queryset.filter(num_keystones=len(keystones))
    return queryset


def _filter_unique_items(queryset: QuerySet, filter_form: GuideListFilterForm) -> QuerySet:
    unique_item_keys = filter_form.cleaned_data['unique_items']
    if unique_item_keys:
        unique_item_choices = dict(filter_form.fields['unique_items'].choices)
        unique_items = [unique_item_choices[int(unique_item_key)] for unique_item_key in unique_item_keys]
        queryset = queryset.filter(unique_items__name__in=unique_items)
        queryset = queryset.annotate(num_unique_items=Count('unique_items'))
        queryset = queryset.filter(num_unique_items=len(unique_items))
    return queryset


def _get_base_filters(filter_form: GuideListFilterForm, user_id: int) -> list[Q]:
    data = filter_form.cleaned_data
    filters = [
        Q(title__icontains=data['title']),
        Q(author__user__username__icontains=data['author_username']),
        Q(modification_datetime__gte=data['updated_after']),
    ]
    if data['base_class_name'] != '0':
        filters.append(Q(ascendancy_class__base_class_name=data['base_class_name']))
    if data['asc_class_name'] != '0':
        filters.append(Q(ascendancy_class__name=data['asc_class_name']))

    if user_id != 0:
        liked = data['liked_by_me']
        if liked is True:
            filters.append(Q(guidelike__user__user_id=user_id) & Q(guidelike__is_active=True))
        if liked is False:
            filters.append(~Q(guidelike__user__user_id=user_id) | Q(guidelike__is_active=False))

    if (value := int(data['active_skill'])) != 0:
        skill_name = dict(filter_form.fields['active_skill'].choices)[value]
        filters.append(Q(primary_skills__name=skill_name))
    return filters


def _apply_order(queryset: QuerySet, filter_form: GuideListFilterForm) -> QuerySet:
    order_by = filter_form.cleaned_data['order_by']
    order_field_map = {
        'Trending': ['-likes_recently', 'title'],
        'Popular': ['-likes', 'title'],
        'Modification date': ['-modification_datetime', 'title'],
        'Creation date': ['-creation_datetime', 'title'],
        'Title': ['title'],
    }
    return queryset.order_by(*order_field_map[order_by])
