from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Course, Question, Choice, Submission


@login_required
def submit(request, course_id):
    """
    Submit the exam for a particular course.

    - Gets all questions belonging to the course
    - Checks the selected answers
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

        # Total number of questions
        total_questions = questions.count()

        # Initial score
        score = 0

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

                # Check whether the answer is correct
                is_correct = selected_choice.is_correct

                # Increase score if correct
                if is_correct:
                    score += 1

                # Save submission
                Submission.objects.create(
                    user=request.user,
                    question=question,
                    selected_choice=selected_choice,
                    is_correct=is_correct
                )

        # Redirect to result page
        return redirect(
            "show_exam_result",
            course_id=course.id
        )

    # If request is not POST
    return redirect("/")


@login_required
def show_exam_result(request, course_id):
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

    # Get submissions made by the current user
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

    # Calculate score
    score = submissions.filter(
        is_correct=True
    ).count()

    # Calculate percentage
    percentage = 0

    if total_questions > 0:
        percentage = (score / total_questions) * 100

    # Data sent to template
    context = {
        "course": course,
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
