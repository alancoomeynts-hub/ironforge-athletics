from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from community.models import Comment, Post
from membership.models import Membership, MembershipType


class CommunityViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alan",
            email="alan@example.com",
            password="testpass123",
        )

        membership_type = MembershipType.objects.create(
            name="Standard",
            slug="standard",
            price=29.99,
            stripe_price_id="price_test_123",
            is_available=True,
        )

        Membership.objects.create(
            user=self.user,
            membership_type=membership_type,
            status=Membership.Status.ACTIVE,
        )

        self.client.login(
            username="alan",
            password="testpass123",
        )

        self.community_url = reverse("community:community")

        self.post = Post.objects.create(
            author=self.user,
            title="Test post",
            slug="test-post",
            content="This is a test post.",
            status=Post.Status.PUBLISHED,
        )

    def test_community_board_requires_login(self):
        self.client.logout()

        response = self.client.get(self.community_url)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_community_board_renders_published_posts(self):
        response = self.client.get(self.community_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "community/community.html")
        self.assertIn(
            self.post,
            response.context["published_posts"].object_list,
        )

    def test_post_detail_hides_draft_from_other_users(self):
        draft = Post.objects.create(
            author=self.user,
            title="Draft post",
            slug="draft-post",
            content="Draft content.",
            status=Post.Status.DRAFT,
        )

        other_user = User.objects.create_user(
            username="sarah",
            email="sarah@example.com",
            password="testpass123",
        )

        self.client.logout()
        self.client.login(
            username="sarah",
            password="testpass123",
        )

        response = self.client.get(
            reverse(
                "community:post",
                args=[draft.pk, draft.slug],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_create_post_publishes_post(self):
        response = self.client.post(
            reverse("community:create_post"),
            {
                "title": "My new post",
                "content": "This is my new post.",
                "action": "publish",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)

        post = Post.objects.get(title="My new post")

        self.assertEqual(post.status, Post.Status.PUBLISHED)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.slug, "my-new-post")

    def test_author_can_edit_own_post(self):
        response = self.client.post(
            reverse(
                "community:edit_post",
                args=[self.post.pk],
            ),
            {
                "title": "Updated title",
                "content": "Updated content.",
            },
            follow=True,
        )

        self.post.refresh_from_db()

        self.assertEqual(self.post.title, "Updated title")

    def test_author_can_delete_own_post(self):
        response = self.client.post(
            reverse(
                "community:delete_post",
                args=[self.post.pk],
            ),
            follow=True,
        )

        self.assertFalse(Post.objects.filter(pk=self.post.pk).exists())

    def test_member_can_add_comment(self):
        response = self.client.post(
            reverse(
                "community:add_comment",
                args=[self.post.pk],
            ),
            {
                "content": "Great post!",
            },
            follow=True,
        )

        comment = Comment.objects.filter(post=self.post).first()

        self.assertIsNotNone(comment)
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.content, "Great post!")
