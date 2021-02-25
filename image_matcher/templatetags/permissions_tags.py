from django import template


register = template.Library()


@register.filter(name='has_ebay_tokens')
def has_ebay_tokens(user):
    """Returns true if user already has already signed up through ebay."""
    if not user.is_authenticated:
        return False
    return True if user.user_tokens_profile.refresh_token else False

