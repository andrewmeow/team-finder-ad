import json
from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import (CreateView, DetailView, ListView,
                                  RedirectView, UpdateView)

from projects.forms import ProjectForm
from projects.models import Project, Skill
from team_finder.constants import (AUTOCOMPLETE_LIMIT, CLOSED_STATUS,
                                   OPEN_STATUS, PAGINATE_BY)


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('projects:project_list')


class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create-project.html'

    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context

    def get_success_url(self):
        return reverse('projects:project-details', kwargs={'pk': self.object.pk})


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'projects/project-details.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_id'] = 'project'
        return context


class ProjectListView(ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        queryset = super().get_queryset()
        skill_filter = self.request.GET.get('skill')
        if skill_filter:
            queryset = queryset.filter(skills__name=skill_filter)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        skill_name = self.request.GET.get('skill', '')
        active_skill = None
        if skill_name:
            try:
                active_skill = Skill.objects.get(name=skill_name)
            except Skill.DoesNotExist:
                pass
        context['all_skills'] = Skill.objects.all()
        # теперь объект Skill или None
        context['active_skill'] = active_skill
        return context


class ProjectCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return JsonResponse({'status': 'error', 'message': 'Недостаточно прав'},
                                status=HTTPStatus.FORBIDDEN)
        if project.status != OPEN_STATUS:
            return JsonResponse({'status': 'error', 'message': 'Проект уже завершён'},
                                status=HTTPStatus.BAD_REQUEST)
        project.status = CLOSED_STATUS
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': CLOSED_STATUS})


class ProjectToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        user = request.user
        if project.owner == user:
            return JsonResponse(
                {'status': 'error',
                 'message': 'Владелец не может участвовать в своём проекте'},
                status=HTTPStatus.BAD_REQUEST)

        if project.participants.filter(pk=user.pk).exists():
            project.participants.remove(user)
            is_participant = False
        else:
            project.participants.add(user)
            is_participant = True

        return JsonResponse({
            'status': 'ok',
            'participant': is_participant,
        })


class SkillAutocompleteView(View):
    def get(self, request):
        query = request.GET.get('q', '').strip()
        if not query:
            return JsonResponse([], safe=False)
        skills = Skill.objects.filter(
            name__istartswith=query).order_by('name')[:AUTOCOMPLETE_LIMIT]
        data = [{'id': skill.id, 'name': skill.name} for skill in skills]
        return JsonResponse(data, safe=False)


class ProjectSkillAddView(LoginRequiredMixin, View):
    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return JsonResponse({'error': 'Недостаточно прав'},
                                status=HTTPStatus.FORBIDDEN)
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Некорректный JSON'},
                                status=HTTPStatus.BAD_REQUEST)

        skill_id = data.get('skill_id')
        name = data.get('name')

        if not skill_id and not name:
            return JsonResponse({'error': 'Необходимо передать skill_id или name'},
                                status=HTTPStatus.BAD_REQUEST)

        created = False
        if skill_id:
            skill = get_object_or_404(Skill, pk=skill_id)
        else:
            skill, created = Skill.objects.get_or_create(name=name.strip())

        if project.skills.filter(pk=skill.pk).exists():
            added = False
        else:
            project.skills.add(skill)
            added = True

        return JsonResponse({
            'id': skill.id,
            'name': skill.name,
            'created': created,
            'added': added,
        })


class ProjectSkillRemoveView(LoginRequiredMixin, View):
    def post(self, request, pk, skill_id):
        project = get_object_or_404(Project, pk=pk)
        if project.owner != request.user:
            return JsonResponse({'error': 'Недостаточно прав'},
                                status=HTTPStatus.FORBIDDEN)

        skill = get_object_or_404(Skill, pk=skill_id)
        if not project.skills.filter(pk=skill.pk).exists():
            return JsonResponse({'error': 'Навык не привязан к проекту'},
                                status=HTTPStatus.BAD_REQUEST)

        project.skills.remove(skill)
        return JsonResponse({'status': 'ok'})


class HomeRedirectView(RedirectView):
    pattern_name = 'projects:project_list'
