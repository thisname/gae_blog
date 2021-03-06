from google.appengine.api import mail, memcache

from base import BaseController, renderIfCachedNoErrors

from gae_blog.formencode.validators import UnicodeString, Email, URL

class PostController(BaseController):
    """ shows an individual post and saves comments to it """

    @renderIfCachedNoErrors
    def get(self, post_slug):

        if post_slug:
            blog = self.getBlog()
            post = self.model.BlogPost.get_by_key_name(post_slug, parent=blog)
            if post and post.published:
                # only display a post if it's actually published
                form_data, errors = self.errorsFromSession()
                return self.cacheAndRenderTemplate('post.html', post=post, form_data=form_data, errors=errors)

        return self.renderError(404)

    def post(self, post_slug):

        ip_address = self.request.remote_addr
        blog = self.getBlog()
        if blog and blog.enable_comments and ip_address not in blog.blocklist:
            # only allow comment posting if comments are enabled
            if post_slug:
                post = self.model.BlogPost.get_by_key_name(post_slug, parent=blog)
                if post and post.published:
                    # only allow commenting to a post if it's actually published

                    author_choice = self.request.get("author-choice")
                    author_slug = self.request.get("author")
                    name = self.request.get("name")
                    url = self.request.get("url")
                    email = self.request.get("email")
                    body = self.request.get("body", "")

                    errors = {}
                    form_data = {"author-choice": author_choice, "author": author_slug, "name": name, "url": url, "email": email, "body": body}

                    # strip out all HTML to be on the safe side
                    body = self.model.stripHTML(body)

                    # validate
                    body = self.validate(UnicodeString(not_empty=True), body)
                    if body:
                        # turn URL's into links
                        body = self.model.linkURLs(body)
                        # finally, replace linebreaks with HTML linebreaks
                        body = body.replace("\r\n", "<br/>")
                    else:
                        errors["body"] = True

                    if author_choice == "author":
                        # validate that if they want to comment as an author that it's valid and they're approved
                        if not self.isUserAdmin():
                            return self.renderError(403)
                        author = self.model.BlogAuthor.get_by_key_name(author_slug, parent=blog)
                        if not author:
                            errors["author"] = True

                        if errors:
                            self.errorsToSession(form_data, errors)
                            return self.redirect(self.blog_url + '/post/' + post_slug + '#comments')

                        comment = self.model.BlogComment(body=body, approved=True, author=author.key(), parent=post)
                        memcache.delete(self.request.path + self.request.query_string)
                    else:
                        # validate that the email address is valid
                        email = self.validate(Email(), email)
                        if not email: errors["email"] = True

                        # validate that the name, if present, is valid
                        if name:
                            name = self.model.stripHTML(name)
                            name = self.validate(UnicodeString(max=500), name)
                            if not name: errors["name"] = True

                        # validate that the url, if present, is valid
                        if url:
                            url = self.validate(URL(add_http=True), url, "URL")
                            if not url: errors["url"] = True

                        if errors:
                            self.errorsToSession(form_data, errors)
                            return self.redirect(self.blog_url + '/post/' + post_slug + '#comments')

                        # look for a previously approved comment from this email address on this blog
                        approved = blog.comments.filter("email =", email).filter("approved =", True)

                        comment = self.model.BlogComment(email=email, body=body, ip_address=ip_address, parent=post)
                        if name:
                            comment.name = name
                        if url:
                            comment.url = url

                        if approved.count():
                            comment.approved = True
                            memcache.delete(self.request.path + self.request.query_string)
                        elif blog.moderation_alert and blog.admin_email:
                            # send out an email to the author of the post if they have an email address
                            # informing them of the comment needing moderation
                            author = post.author
                            if author.email:
                                if blog.title:
                                    subject = blog.title + " - Comment Awaiting Moderation"
                                else:
                                    subject = "Blog - Comment Awaiting Moderation"
                                comments_url = "http://" + self.request.headers.get('host', '') + self.blog_url + "/admin/comments"
                                body = "A comment on your post \"" + post.title + "\" is waiting to be approved or denied at " + comments_url
                                mail.send_mail(sender=blog.admin_email, to=author.name + " <" + author.email + ">", subject=subject, body=body)

                    comment.put()

                    return self.redirect(self.blog_url + '/post/' + post_slug + '#comments')

        return self.renderError(404)

