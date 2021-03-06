from google.appengine.api import mail

from base import BaseController, renderIfCachedNoErrors

from gae_blog.formencode.validators import UnicodeString, Email

class ContactController(BaseController):
    """ handles request for the contact page of the site """

    @renderIfCachedNoErrors
    def get(self, sent=False):

        blog = self.getBlog()

        if not blog or not blog.contact:
            return self.renderError(403)

        authors = [author for author in blog.authors if author.email]

        form_data, errors = self.errorsFromSession()

        return self.cacheAndRenderTemplate('contact.html', sent=sent, authors=authors, form_data=form_data, errors=errors, page_title="Contact")

    def post(self, sent=False):

        blog = self.getBlog()
        if blog and blog.contact:
            author_slug = self.request.get("author")
            email = self.request.get("email")
            subject = self.request.get("subject", "")
            body = self.request.get("body")

            errors = {}
            form_data = {"author": author_slug, "email": email, "subject": subject, "body": body}

            # validation and handling
            email = self.validate(Email(), email)
            if not email: errors["email"] = True

            subject = self.validate(UnicodeString(), subject)
            if subject is None: errors["subject"] = True
            if blog.title:
                subject = blog.title + " - Contact Form Message: " + subject
            else:
                subject = "Blog - Contact Form Message: " + subject

            body = self.validate(UnicodeString(not_empty=True), body)
            if not body: errors["body"] = True

            if author_slug == "all":
                authors = [author for author in blog.authors if author.email]
                if not authors:
                    errors["author_slug"] = True
            else:
                author = self.model.BlogAuthor.get_by_key_name(author_slug, parent=blog)
                if not author or not author.email:
                    errors["author_slug"] = True
                authors = [author]

            if errors:
                self.errorsToSession(form_data, errors)
                return self.redirect(self.blog_url + '/contact/')

            if blog.admin_email:
                for author in authors:
                    mail.send_mail(sender=blog.admin_email, reply_to=email, to=author.name + " <" + author.email + ">", subject=subject, body=body)

        return self.redirect(self.blog_url + '/contact/sent')

