from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Course, Question, Choice, Submission


@login_required
def submit(request, course_id):
    """
    Submit the exam for a particular course.

    - Gets all questions belonging to the course
    - Checks the selected answers using is_get_score()
    - Calculates the score
    - Saves each answer as a Submission
    - Redirects to the result page
    """

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":

        # Get all questions for this course
        questions = Question.objects.filter(
            lesson__course=course
        )

        # Remove previous submissions of this user for this course
        Submission.objects.filter(
            user=request.user,
            question__lesson__course=course
        ).delete()

        # Process every question
        for question in questions:

            # Get selected choice from submitted form
            selected_choice_id = request.POST.get(
                f"question_{question.id}"
            )

            # If user selected an answer
            if selected_choice_id:

                # Get the selected choice
                selected_choice = get_object_or_404(
                    Choice,
                    id=selected_choice_id,
                    question=question
                )

                # Check answer using the required method
                is_correct = question.is_get_score(
                    selected_choice
                )

                # Save submission
                Submission.objects.create(
                    user=request.user,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )

        # Get the latest submission for this course
        latest_submission = Submission.objects.filter(
            user=request.user,
            question__lesson__course=course
        ).order_by("-submitted_at").first()

        # Redirect to result page
        return redirect(
            "show_exam_result",
            course_id=course.id,
            submission_id=latest_submission.id
        )

    # If request is not POST
    return redirect("/")


@login_required
def show_exam_result(request, course_id, submission_id):
    """
    Display the exam result for the logged-in user.

    Calculates:
    - Score
    - Total questions
    - Percentage
    - Individual question results
    """

    # Get course
    course = get_object_or_404(
        Course,
        id=course_id
    )

    # Get the selected submission
    submission = get_object_or_404(
        Submission,
        id=submission_id,
        user=request.user
    )

    # Get all submissions made by the current user
    # for this course
    submissions = Submission.objects.filter(
        user=request.user,
        question__lesson__course=course
    ).select_related(
        "question",
        "selected_choice"
    )

    # Get total number of questions
    total_questions = Question.objects.filter(
        lesson__course=course
    ).count()

    # Calculate score using is_get_score()
    score = 0

    for item in submissions:
        if item.question.is_get_score(
            item.selected_choice
        ):
            score += 1

    # Calculate percentage
    percentage = 0

    if total_questions > 0:
        percentage = (score / total_questions) * 100

    # Data sent to template
    context = {
        "course": course,
        "submission": submission,
        "submissions": submissions,
        "score": score,
        "total_questions": total_questions,
        "percentage": percentage,
    }

    # Render result page
    return render(
        request,
        "exam_result.html",
        context
    )
