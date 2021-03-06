Copyright &copy; 2010, [Brendan Doms](http://www.bdoms.com/)
Licensed under the [MIT license](http://www.opensource.org/licenses/MIT)


GAE Blog is a project to provide a bare-bones blogging solution for Google App
Engine that makes no assumptions, and is easy to integrate with existing apps.

It uses and includes a copy of [Mako](http://www.makotemplates.org/)


## Setup for Integrating with Your Project

In your pre-existing application add this project as a submodule, like so:

```bash
git submodule add git://github.com/bdoms/gae_blog.git gae_blog
```

Next, you need to initialize and update the submodule to get all the submodules
that exist within the gae_blog project:

```bash
cd gae_blog
git submodule init
git submodule update
```

Then repeat for your project:

```bash
cd ..
git submodule init
git submodule update
```

Finally, you need to merge the libraries and handlers from the example GAE Blog
`app.yaml` into your project's top level `app.yaml`. After doing that, starting
the development server and going to `/blog` will be handled by `gae_blog`.

Go to `/blog/admin` to configure your blog, post to it, and moderate comments.


## Setup for Using As a Parent Project

If you just want the blog to be the only part of your website, the process is
fairly similar. Just clone (or fork) the repository and you should be good.


## Managing Multiple Blogs

If you want to use GAE Blog for multiple blogs within the same project/domain,
you just have to decide on a relative URL for each one (`/blog` by default)
and modify these things:

 * add handlers for it to your `app.yaml` as mentioned above
 * add it to the `BLOG_URLS` list in `blog.py`
 * create each blog with its respective URL from `/blog/admin`


## Using a Custom Base Template

You can obviously modify the included base template as much as you want, but in
order to avoid redundancy, if you already have a Mako one that you'd like to
use all you have to do is modify the "Base Template" configuration option on
the blog admin page (at `/blog/admin`) with a path relative to your project (i.e.
the parent directory of the `gae_blog` folder). For example, if your directory
structure looks like this:

 - your_project
   - gae_blog
   - your_templates
     - your_base_template.html

You would enter "your_templates/your_base_template.html" as the relative path.
However, if you leave that option blank, then the `default_base.html` file will
be used instead.

