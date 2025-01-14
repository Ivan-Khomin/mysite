from django import forms
from .models import Post


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'nameInput'
    }))
    email = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'exampleInputEmail1',
        'aria-describedby': 'emailHelp'
    }))
    to = forms.EmailField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'id': 'emailTo',
    }))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={
        'class': 'form-control',
        'id': 'comments',
        'rows': '3'
    }))


class CommentForm(forms.Form):
    name = forms.CharField(max_length=25, widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'id': 'nameInput'
        }
    ))
    email = forms.EmailField(widget=forms.TextInput(
        attrs={
            'class': 'form-control',
            'id': 'exampleInputEmail1',
            'aria-describedby': 'emailHelp'
        }
    ))
    comment = forms.CharField(required=False, widget=forms.Textarea(
        attrs={
            'class': 'form-control',
            'id': 'comments',
            'rows': '3'
        }
    ))


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'id': 'inputLogin',
        'class': 'form-control',
        'placeholder': 'Логін'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'type': 'password',
        'id': 'inputPassword',
        'class': 'form-control',
        'placeholder': 'Пароль'
    }))


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'short_description', 'image', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'titleInput'
            }),
            'short_description': forms.Textarea(attrs={
                'class': 'form-control',
                'id': 'shortDescriptionText'
            }),
            'image': forms.ClearableFileInput(attrs={
                'id': 'imageFile'
            }),
            'tags': forms.TextInput(attrs={
                'class': 'form-control',
                'id': 'tagsInput'
            })
        }
