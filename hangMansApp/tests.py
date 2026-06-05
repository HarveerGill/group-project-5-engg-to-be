from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Game, Word


class HangmanSecurityTests(TestCase):
    def setUp(self):
        self.word = Word.objects.create(word='test')
        self.user = User.objects.create_user(username='harveer', password='Password123')
        self.other_user = User.objects.create_user(username='other', password='Password123')

    def test_history_requires_login(self):
        # Requirement: only logged-in users can view score history.
        response = self.client.get(reverse('history'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_password_is_hashed(self):
        # Requirement: passwords must not be stored in plain text.
        user = User.objects.create_user(username='test', password='Password123')
        self.assertNotEqual(user.password, 'Password123')
        self.assertTrue(user.password.startswith('pbkdf2_'))

    def test_login_success(self):
        result = self.client.login(username='harveer', password='Password123')
        self.assertTrue(result)

    def test_user_only_sees_own_scores(self):
        # Requirement: authenticated users can view their own scores only.
        own_game = Game.objects.create(user=self.user, word=self.word, session='s1', win=True)
        other_game = Game.objects.create(user=self.other_user, word=self.word, session='s2', win=False)
        self.client.login(username='harveer', password='Password123')
        response = self.client.get(reverse('history'))
        self.assertContains(response, f'Game {own_game.id}')
        self.assertNotContains(response, f'Game {other_game.id}')

    def test_update_word_rejects_invalid_letter(self):
        # Requirement: server-side allow-list validation prevents malformed input.
        response = self.client.post(reverse('updated-word-game'), {
            'wordId': self.word.id,
            'gameId': 0,
            'letter': '<script>',
        })
        self.assertEqual(response.status_code, 400)

    def test_update_word_creates_owned_score_for_logged_in_user(self):
        # Requirement: game records created while logged in are linked to that user.
        self.client.login(username='harveer', password='Password123')
        response = self.client.post(reverse('updated-word-game'), {
            'wordId': self.word.id,
            'gameId': 0,
            'letter': 't',
        })
        self.assertEqual(response.status_code, 200)
        game_id = response.json()['gameId']
        self.assertEqual(Game.objects.get(id=game_id).user, self.user)

    def test_update_word_blocks_cross_user_tampering(self):
        # Requirement: users must not update another user's score/game record.
        game = Game.objects.create(user=self.other_user, word=self.word, session='s2')
        self.client.login(username='harveer', password='Password123')
        response = self.client.post(reverse('updated-word-game'), {
            'wordId': self.word.id,
            'gameId': game.id,
            'letter': 't',
        })
        self.assertEqual(response.status_code, 403)

    def test_share_score_is_read_only_and_public(self):
        # Requirement: non-users can view a shared score without edit/delete capability.
        game = Game.objects.create(user=self.user, word=self.word, session='s1', win=True)
        response = self.client.get(reverse('share-score', args=[game.share_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Shared Hangman Score')
        self.assertNotContains(response, 'delete')

    def test_hint_limited_to_one_per_game(self):
        # Feature requirement: one-use hint limit reduces word enumeration abuse.
        self.client.login(username='harveer', password='Password123')
        game = Game.objects.create(user=self.user, word=self.word, session='s1')
        first = self.client.post(reverse('hint'), {'gameId': game.id})
        second = self.client.post(reverse('hint'), {'gameId': game.id})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)

    def test_hint_blocks_cross_user_tampering(self):
        # Feature requirement: hint endpoint enforces the same ownership rule as score updates.
        game = Game.objects.create(user=self.other_user, word=self.word, session='s2')
        self.client.login(username='harveer', password='Password123')
        response = self.client.post(reverse('hint'), {'gameId': game.id})
        self.assertEqual(response.status_code, 403)

    def test_difficulty_allow_list_falls_back_safely(self):
        # Feature requirement: difficulty input is constrained to a safe allow-list.
        response = self.client.get('/?difficulty=<script>')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Difficulty')
