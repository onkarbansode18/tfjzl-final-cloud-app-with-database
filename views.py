from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Course, Question, Choice, Submission


@login_required
def submit(request, course_id):
    """
    Submit the assessment for a course and calculate the score.
    """

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":

        questions = Question.objects.filter(
            lesson__course=course
        )

        score = 0
        total_questions = questions.count()

        # Remove previous submissions for this course
        Submission.objects.filter(
            user=request.user,
            question__lesson__course=course
        ).delete()

        # Check each question
        for question in questions:

            selected_choice_id = request.POST.get(
                f"question_{question.id}"
            )

            if selected_choice_id:

                selected_choice = get_object_or_404(
                    Choice,
                    id=selected_choice_id,
                    question=question
                )

                is_correct = selected_choice.is_correct

                if is_correct:
                    score += 1

                Submission.objects.create(
                    user=request.user,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )

        return redirect(
            "show_exam_result",
            course_id=course.id
        )

    return redirect("/")


@login_required
def show_exam_result(request, course_id):
    """
    Display the exam result for the logged-in user.
    """

    course = get_object_or_404(Course, id=course_id)

    submissions = Submission.objects.filter(
        user=request.user,
        question__lesson__course=course
    ).select_related(
        "question",
        "selected_choice"
    )

    total_questions = Question.objects.filter(
        lesson__course=course
    ).count()

    score = submissions.filter(
        is_correct=True
    ).count()

    percentage = 0

    if total_questions > 0:
        percentage = (score / total_questions) * 100

    context = {
        "course": course,
        "submissions": submissions,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
    }

    return render(
        request,
        "exam_result.html",
        context
    )
