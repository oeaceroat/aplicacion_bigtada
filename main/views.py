from django.shortcuts import render

# Create your views here.

def index(request):
    #latest_question_list = Question.objects.order_by('-pub_date')[:5]
    context = {}
    #context = {
    #    'latest_question_list': latest_question_list,
    #}

    return render(request, 'main/index.html', context)
