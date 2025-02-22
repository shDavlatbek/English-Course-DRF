from modeltranslation.translator import TranslationOptions, translator
from main import models



# class MainSlideTranslationOptions(TranslationOptions):
#     fields = ('title', 'description')
#     required_languages = {
#         'ru': ('title', 'description',), 
#         'en': ('title', 'description',), 
#         'default': ('title', 'description',)
#     }

#     fallback_languages = {
#         'ru': ('title', 'description',), 
#         'en': ('title', 'description',), 
#         'default': ('title', 'description',)
#     }

# translator.register(MainSlide, MainSlideTranslationOptions)