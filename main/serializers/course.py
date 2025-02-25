from rest_framework import serializers
from main.models import Category, Quiz, Question, Option, QuizResult, Course

class AnswerSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    option = serializers.IntegerField()

class QuizResultProcessSerializer(serializers.Serializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    answers = AnswerSerializer(many=True)

    def create(self, validated_data):
        user = self.context['request'].user
        quiz = validated_data['quiz']
        answers = validated_data['answers']

        total_questions = quiz.questions.count()
        correct_count = 0

        # Process each answer
        for answer in answers:
            # Ensure the question is part of the quiz
            try:
                question = quiz.questions.get(pk=answer['question'])
            except Question.DoesNotExist:
                raise serializers.ValidationError(
                    f"Question id {answer['question']} is not part of the quiz."
                )

            # Ensure the option is valid for this question
            try:
                option = question.options.get(pk=answer['option'])
            except Option.DoesNotExist:
                raise serializers.ValidationError(
                    f"Option id {answer['option']} is not valid for question id {question.id}."
                )

            if option.is_correct:
                correct_count += 1

        # Calculate score as a percentage
        score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        quiz_result = QuizResult.objects.create(user=user, quiz=quiz, score=score, correct_answers=correct_count)
        return quiz_result



class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']


class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']


class QuizResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizResult
        fields = ['score', 'correct_answers', 'completed_at']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    result = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ('id', 'title', 'description', 'created_at', 'result', 'is_completed', 'questions')

    def get_result(self, obj):
        """
        Retrieve the user's quiz result if they are authenticated.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            quiz_result = obj.results.filter(user=request.user).first()
            if quiz_result:
                return QuizResultSerializer(quiz_result).data
        return None

    def get_is_completed(self, obj):
        """
        Check if the user has completed the quiz if they are authenticated.
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.results.filter(user=request.user).exists()
        return False



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description']


class CourseSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'level', 'image', 'category', 'description',]


class CourseDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    quizzes = QuizSerializer(many=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'image', 'category', 'description', 'content', 'quizzes']



class CourseForCatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        # If Course doesn't actually have a 'level' field, remove it from the list.
        fields = ['id', 'title', 'slug', 'level', 'image', 'description']
        
        

class CategoryDetailSerializer(serializers.ModelSerializer):
    courses = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'courses']

    def get_courses(self, obj):
        request = self.context.get('request')
        level = request.query_params.get('level') if request else None
        qs = obj.courses.all()
        if level:
            qs = qs.filter(level=level)
        # Use CourseForCatSerializer instead of CategoryDetailSerializer here
        return CourseForCatSerializer(qs, many=True, context=self.context).data