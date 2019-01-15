# -*- coding: utf-8 -*-

import secrets

from .models import UserDetail


# Tools needed for effective implementations.

def can_add_question(request):
    """Is user allowed to add new question(s)?
    No student is permitted to add questions neither is an unauthenticated/inactive user allowed too.

    System Administrators and the over all Site Manager(s) are allowed to perform nearly any action on the site."""

    try:
        u_d = UserDetail.objects.get(user=request.user.username)
    except:
        u_d = False
    if request.user.is_superuser:
        return True
    elif u_d or not request.user.is_authenticated:
        return False
    return False


def can_modify(request, creator):
    # Is user allowed to modify something?
    if request.user.is_superuser:
        return True
    elif request.user.username == creator and request.user.is_active:
        return True
    else: return False
    


def can_like(request):
    return True if request.user.is_active else False



def grade(score, int_grade=False):
    score = int(score)
    if int_grade:
        if score >= 70:
            return 5
        elif score >= 60:
            return 4
        elif score >= 50:
            return 3
        elif score >= 40:
            return 2
        elif score >= 35:
            return 1
        else: return 0
    
    else:
        if score >= 70:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 50:
            return "C"
        elif score >= 40:
            return "D"
        elif score >= 35:
            return "E"
        else: return "F"


def gpa(data):
    tp = 0 # total point
    tu = 0 # total course unit
    for c in data:
        tp += data[c][1] * grade(data[c][0])
        tu += data[c][1]
    return (round(tp/tu, 2), [tp, tu])


def cgpa(result1, result2):
    print(result1[0]+result2[0])
    return round((result1[0]+result2[0]) / (result1[1]+result2[1]), 2)



def token(n=10):
    """Generates URL-safe random characters"""
    return secrets.token_urlsafe(n)[:10] # Returns upto 10 characters max.




'''
def can_delete(request, creator):
    # Is user allowed to delete object?
    if request.user.is_superuser:
        return True
    elif request.user == creator and request.user.is_active:
        return True
    else: return False
    

def get_or_create_guest(request):
    ip = request.META["REMOTE_ADDR"] or request.META["X_FORWARDED_FOR"]
    agent = request.META["HTTP_USER_AGENT"]
    try:
        guest = Guest.objects.create(ip=ip, agent=agent)
    except:
        guest = Guest.objects.filter(ip=ip, agent=agent)
        for g in guest:
            if g.ip == ip and g.agent == agent:
                guest = g
                break
    
    return guest.ip+":"+str(guest.id)



def view(request, viewed, t=None):
    """t=type of object to view: 1=view user, 2=view question."""
    if request.user.is_authenticated:
        user = request.user
    else:
        user = get_or_create_guest(request)
    
    if t == 1:
        viewed = UserView.objects.create(user=user, views=viewed)
    if t == 2:
        question = Question.objects.get(pk=viewed)
        viewed = QuestionView.objects.create(user=user, views=question)
    
    return user
'''