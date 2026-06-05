import random
import re

from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from hangMansApp import models

LETTER_RE = re.compile(r'^[a-z]$')
DIFFICULTY_LENGTHS = {
    'easy': (1, 5),
    'medium': (6, 8),
    'hard': (9, 255),
}


def _get_session_key(request):
    """Return a server-side session key instead of trusting a client-controlled CSRF cookie."""
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _word_queryset_for_difficulty(difficulty):
    """Part 3 feature 2: safe difficulty filtering using a fixed allow-list of values."""
    qs = models.Word.objects.all()
    if difficulty in DIFFICULTY_LENGTHS:
        min_len, max_len = DIFFICULTY_LENGTHS[difficulty]
        ids = [w.id for w in qs if min_len <= len(w.word) <= max_len]
        if ids:
            return models.Word.objects.filter(id__in=ids)
    return qs


def _random_word(queryset=None):
    queryset = queryset or models.Word.objects.all()
    ids = list(queryset.values_list('id', flat=True))
    if not ids:
        raise models.Word.DoesNotExist('No words are available in the database.')
    return models.Word.objects.get(id=random.choice(ids))


@ensure_csrf_cookie
def Start(request):
    """Render a new game. The CSRF cookie is explicitly set for secure AJAX POST requests."""
    difficulty = request.GET.get('difficulty', 'medium')
    word = _random_word(_word_queryset_for_difficulty(difficulty))
    word_for_friend = _random_word()
    word_array = ['' for _ in word.word]
    domain = get_current_site(request)
    return render(request, 'index.html', {
        'wordId': word.id,
        'word': word_array,
        'fault': 1,
        'wordForFriend': word_for_friend,
        'domain': domain,
        'difficulty': difficulty if difficulty in DIFFICULTY_LENGTHS else 'medium',
    })


@require_POST
def updateWord(request):
    """Update game state after a guessed letter.

    Secure coding principles applied for Tasks 7 and 9:
    - POST + CSRF is used for state-changing requests.
    - User input is allow-list validated before database access.
    - Game ownership is enforced for authenticated users and anonymous sessions.
    - Object existence/tampering is handled with controlled 400/403 responses.
    """
    word_id = request.POST.get('wordId', '')
    game_id = request.POST.get('gameId', '0')
    letter = (request.POST.get('letter', '') or '').lower()

    if not word_id.isdigit() or not game_id.isdigit() or not LETTER_RE.match(letter):
        return JsonResponse({'error': 'Invalid request.'}, status=400)

    word = get_object_or_404(models.Word, id=int(word_id))
    session = _get_session_key(request)

    game = None
    if int(game_id) > 0:
        qs = models.Game.objects.filter(id=int(game_id), word=word)
        if request.user.is_authenticated:
            qs = qs.filter(user=request.user)
        else:
            qs = qs.filter(session=session, user__isnull=True)
        game = qs.first()
        if game is None:
            return JsonResponse({'error': 'Game not found or access denied.'}, status=403)

    if game is None:
        game = models.Game.objects.create(
            session=session,
            word=word,
            user=request.user if request.user.is_authenticated else None,
        )

    if game.fault >= 6:
        return JsonResponse({'lose': True, 'word': word.word.upper(), 'gameId': game.id})

    word_array = []
    if letter in word.word:
        if letter not in game.letterKnows:
            game.letterKnows += letter
        for char in word.word:
            word_array.append(char if char in game.letterKnows else '')
        if list(word.word) == word_array:
            game.win = True
            game.save()
            return JsonResponse({
                'win': True,
                'wordArray': word_array,
                'gameId': game.id,
                'shareUrl': request.build_absolute_uri(f'/score/{game.share_id}/'),
            })
        game.save()
        return JsonResponse({'gameId': game.id, 'fault': 0, 'wordArray': word_array, 'win': False, 'letter': letter})

    game.fault += 1
    game.save()
    if game.fault >= 6:
        return JsonResponse({
            'lose': True,
            'word': word.word.upper(),
            'gameId': game.id,
            'shareUrl': request.build_absolute_uri(f'/score/{game.share_id}/'),
        })
    return JsonResponse({'gameId': game.id, 'fault': min(game.fault + 1, 7), 'win': False, 'letter': letter})


@require_POST
def get_hint(request):
    """Part 3 feature 1: reveal one safe hint per game while enforcing ownership and input validation."""
    game_id = request.POST.get('gameId', '0')
    if not game_id.isdigit() or int(game_id) <= 0:
        return JsonResponse({'error': 'Start a game before requesting a hint.'}, status=400)

    session = _get_session_key(request)
    qs = models.Game.objects.filter(id=int(game_id))
    if request.user.is_authenticated:
        qs = qs.filter(user=request.user)
    else:
        qs = qs.filter(session=session, user__isnull=True)
    game = qs.select_related('word').first()
    if game is None:
        return JsonResponse({'error': 'Game not found or access denied.'}, status=403)
    if game.hints_used >= 1:
        return JsonResponse({'error': 'Only one hint is allowed per game.'}, status=429)

    hidden_letters = sorted(set(game.word.word) - set(game.letterKnows))
    if not hidden_letters:
        return JsonResponse({'error': 'No hint is available.'}, status=400)

    hint = random.choice(hidden_letters)
    game.letterKnows += hint
    game.hints_used += 1
    game.save()

    word_array = [char if char in game.letterKnows else '' for char in game.word.word]
    return JsonResponse({'hint': hint, 'wordArray': word_array, 'gameId': game.id})


@require_GET
def playShare(request, uui):
    """Allow a non-user to start a game from a UUID word link without exposing database IDs."""
    word_for_friend = _random_word()
    word = get_object_or_404(models.Word, uui=uui)
    word_array = ['' for _ in word.word]
    domain = get_current_site(request)
    return render(request, 'index.html', {
        'wordId': word.id,
        'word': word_array,
        'fault': 1,
        'wordForFriend': word_for_friend,
        'domain': domain,
        'difficulty': 'shared',
    })


@require_GET
def generateWord(request):
    """Generate a shareable word link using a UUID rather than exposing sequential IDs."""
    word = _random_word()
    domain = get_current_site(request)
    return JsonResponse({'word': word.word, 'domain': str(domain), 'uuid': str(word.uui)})


@login_required
def score_history(request):
    """Authenticated users can view only their own scores; non-users are redirected to login."""
    scores = models.Game.objects.filter(user=request.user).select_related('word')
    return render(request, 'history.html', {'scores': scores})


@require_GET
def share_score(request, share_id):
    """Non-users can view a read-only shared score page; editing/deleting is not exposed."""
    game = get_object_or_404(models.Game.objects.select_related('user', 'word'), share_id=share_id)
    return render(request, 'share_score.html', {'game': game})


def chargeDB():
    """Utility used during local setup to load the supplied word bank."""
    with open('static/Hangman_wordbank.txt') as fich:
        line = fich.readlines()
    array = line[0].split(', ')
    for a in array:
        word = a.replace(' ', '').replace('\n', '')
        if word and models.Word.objects.filter(word=word).count() == 0:
            models.Word.objects.create(word=word)
