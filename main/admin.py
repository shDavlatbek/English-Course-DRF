from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from main import models
import nested_admin



class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category']
    search_fields = ['title', 'category__name']
    list_filter = ['category']
    prepopulated_fields = {'slug': ('title',)}



class CourseStackedInline(admin.StackedInline):
    model = models.Course
    extra = 0

class OptionInline(nested_admin.NestedTabularInline):
    model = models.Option
    extra = 0

class QuestionInline(nested_admin.NestedStackedInline):
    model = models.Question
    inlines = [OptionInline]
    extra = 0

class QuizInline(nested_admin.NestedStackedInline):
    model = models.Quiz
    inlines = [QuestionInline]
    extra = 0
    max_num = 1

@admin.register(models.Course)
class CourseAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuizInline]   
    list_display = ('title', 'category',)
    list_filter = ('category',)
    search_fields = ('title', 'category__name',)
    prepopulated_fields = {'slug': ('title',)}
    
    class Media:
        js = ('https://cdnjs.cloudflare.com/ajax/libs/jquery/3.7.1/jquery.min.js',)


class EnrollmentInline(admin.StackedInline):
    model = models.Enrollment
    extra = 0

class QuizResultInline(admin.StackedInline):
    model = models.QuizResult
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    prepopulated_fields = {'slug': ('name',)}  


class UserCustomAdmin(UserAdmin):
    inlines = [EnrollmentInline, QuizResultInline]


admin.site.register(models.User, UserCustomAdmin)
admin.site.register(models.Category, CategoryAdmin)
# admin.site.register(models.Course, CourseAdmin)

# Register FillInBlankOption as inline for FillInBlankQuestion
class FillInBlankOptionInline(admin.TabularInline):
    model = models.FillInBlankOption
    extra = 3

@admin.register(models.FillInBlankQuestion)
class FillInBlankQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'quiz', 'text_before', 'text_after', 'correct_answer', 'created_at')
    list_filter = ('quiz', 'created_at')
    search_fields = ('text_before', 'text_after', 'correct_answer')
    inlines = [FillInBlankOptionInline]