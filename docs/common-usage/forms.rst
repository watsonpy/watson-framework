.. _common_usage_forms:

Forms
=====

Forms are defined in a declarative way within Watson. This means that you only need to define fields you want without any other boilerplate code.

.. code-block:: python

    from watson import form
    from watson.form import fields

    class Login(form.Form):
        username = fields.Text(label='Username')
        password = fields.Password(label='Password')
        submit = fields.Submit(value='Login', button_mode=True)

Which when implemented in a view would convert:


.. code-block:: html

    <html>
        <body>
            {{ form.open() }}
            {{ form.username.render_with_label() }}
            {{ form.password.render_with_label() }}
            {{ form.submit }}
            {{ form.close() }}
        </body>
    </html>

into...

.. code-block:: html

    <html>
        <body>
            <form>
                <label for="username">Username</label><input type="text" name="username" />
                <label for="password">Password</label><input type="text" name="password" />
                <button type="submit">Login</button>
            </form>
        </body>
    </html>

Field types
-----------

Fields are referenced by their HTML element name. Whenever a field is defined within a form any additional keyword arguments are used as attributes on the element itself. Current fields that are included are:


+------------------------+------------------------+
| Field                  | Output                 |
+========================+========================+
| Input                  | <input type="" />      |
+------------------------+------------------------+
| Button                 | <button></button>      |
+------------------------+------------------------+
| Textarea               | <textarea></textarea>  |
+------------------------+------------------------+
| Select                 | <select></select>      |
+------------------------+------------------------+

There are also a bunch of convenience classes as well which may add additional validators and filters to the field.

+------------------------+----------------------------------------------------+
| Field                  | Output                                             |
+========================+====================================================+
| Input                  | <input type="" />                                  |
+------------------------+----------------------------------------------------+
| Radio                  | <input type="radio" />                             |
+------------------------+----------------------------------------------------+
| Checkbox               | <input type="checkbox" />                          |
+------------------------+----------------------------------------------------+
| Text                   | <input type="text" />                              |
+------------------------+----------------------------------------------------+
| Date                   | <input type="date" />                              |
+------------------------+----------------------------------------------------+
| Email                  | <input type="email" />                             |
+------------------------+----------------------------------------------------+
| Hidden                 | <input type="hidden" />                            |
+------------------------+----------------------------------------------------+
| Csrf                   | <input type="csrf" />                              |
+------------------------+----------------------------------------------------+
| Password               | <input type="password" />                          |
+------------------------+----------------------------------------------------+
| File                   | <input type="file" />                              |
+------------------------+----------------------------------------------------+
| Submit                 | <input type="submit" /> or <button>Submit</button> |
+------------------------+----------------------------------------------------+

These can all be imported from the ``watson.form.fields`` module.

Populating and binding objects to a form
----------------------------------------

Form data can be populated with any standard Python dict.

.. code-block:: python

    form = forms.Login()
    form.data = {'username': 'Simon'}

These values can then be retrieved by:

.. code-block:: python

    form.username  # Simon

Direct access to the form field can be made by:

.. code-block:: python

    form.fields['username']

If the field has been through the validation/filter process, you can still retrieve the original value that was submitted by:

.. code-block:: python

    form.fields['username'].original_value  # Simon

Binding an object to the form
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes it's worth being able to bind an object to the form so that any posted data can automatically be injected into the object. This is a relatively simple task to achieve:

*Object entities*

.. code-block:: python

    class User(object):
        username = None
        password = None
        email = None

*Edit user form*

.. code-block:: python

    from watson import form
    from watson.form import fields

    class User(forms.Form):
        username = fields.Text(label='Username')
        password = fields.Password(label='Password')
        email = fields.Email(label='Email Address')

*Controller responsible for saving the user*

.. code-block:: python

    from watson.framework import controllers
    from app import forms

    class Login(controllers.Rest):
        def POST(self):
            user = User()
            form = forms.User('user')
            form.bind(user)
            form.data = self.request.post
            if form.is_valid():
                user.save()  # save the updated user data

When is_valid() is called the POST'd data will be injected directly into the User object. While this is great for simple CRUD interfaces, things can get more complex when an object contains other objects. To resolve this we have to define a mapping to map the flat post data to the various objects (we only need to define the mapping for data that isn't a direct mapping).

A basic mapping consists of a dict of key/value pairs where the value is a tuple that denotes the object 'tree'.

.. code-block:: python

    mapping = {
        'field_name': ('attribute', 'attribute', 'attribute')
    }

We'll take the same example from above, but modify it slightly so that our User object now also contains a Contact object (note that some of this code such as the entities would be handled automatically by your ORM of choice).

*Object entities*

.. code-block:: python

    class User(object):
        username = None
        password = None
        contact = None

        def __init__(self):
            self.contact = Contact()

    class Contact(object):
        email = None
        phone = None

*Edit user form*

.. code-block:: python

    from watson import form
    from watson.form import fields

    class User(forms.Form):
        username = fields.Text(label='Username')
        password = fields.Password(label='Password')
        email = fields.Email(label='Email Address')
        phone = fields.Email(label='Phone Number')

*Controller responsible for saving the user*

.. code-block:: python

    from watson.framework import controllers
    from app import forms

    class Login(controllers.Rest):
        def POST(self):
            user = User()
            form = forms.User('user')
            form.bind(user, mapping={'email': ('contact', 'email'), 'phone': ('contact', 'phone')})
            form.data = self.request.post
            if form.is_valid():
                user.save()  # save the updated user data

Filters and Validators
----------------------

Filters and validators allow you to sanitize and modify your data prior to being used within your application. By default, all fields have the Trim filter which removes whitespace from the value of the field.

When the is_valid() method is called on the form each field is filtered, and then validated.

To add new validators and filters to a field you simply add them as a keyword argument to the field definition.

.. code-block:: python

    from watson import form
    from watson.form import fields
    from watson import validators

    class Login(form.Form):
        username = fields.Text(label='Username', validators=[validators.Length(min=10)])
        password = fields.Password(label='Password', validators=[validators.Required()])
        # required can actually be set via required=True
        submit = fields.Submit(value='Login', button_mode=True)

For a full list of validators and filters check out filters and validators in the reference library.

Validating post data
--------------------

Validating forms is usually done within a controller. We'll utilize the Login form above to demonstrate this...

.. code-block:: python

    from watson.framework import controllers
    from app import forms

    class Login(controllers.Rest):
        def GET(self):
            form = forms.Login('login_form', action='/login')
            form.data = self.redirect_vars
            # populate the form with POST'd data to avoid the PRG issue
            # we don't really need to do this
            return {
                'form': form
            }

        def POST(self):
            form = forms.Login('login_form')
            form.data = self.request.post
            if form.is_valid():
                self.flash_messages.add('Successfully logged in')
                self.redirect('home')
            else:
                self.redirect('login')

With the above code, when a user hits /login, they are presented with a login form from the GET method of the controller. As they submit the form, the code within the POST method will execute. If the form is valid, then they will be redirected to whatever the 'home' route displays, otherwise they will be redirected back to the GET method again.

Errors upon validating
^^^^^^^^^^^^^^^^^^^^^^

When is_valid() is called, all fields will be filtered and validated, and any subsequent error messages will be available via form.errors.

Protecting against CSRF (Cross site request forgery)
----------------------------------------------------

`Cross site request forgery`_ is a big issue with a lot of code bases. Watson provides a simple way to protect your users against it by using a decorator.

.. code-block:: python

    from watson import form
    from watson.form import fields
    from watson.form.decorators import has_csrf

    @has_csrf
    class Login(form.Form):
        username = fields.Text(label='Username')
        password = fields.Password(label='Password')
        submit = fields.Submit(value='Login', button_mode=True)

The above code will automatically add a new field (named csrf_token) to the form, which then will need to be rendered in your view. You will also need to pass the session into the form when it is instantiated so that the csrf token can be saved against the form.

.. code-block:: python

    from watson.framework import controllers
    from app import forms

    class Login(controllers.Rest):
        def GET(self):
            form = forms.Login('login_form', action='/login', session=self.request.session)
            form.data = self.redirect_vars
            return {
                'form': form
            }

As the form is validated (via is_valid()), the token will automatically be processed against the csrf validator.

Jinja2 Helper Filters and Functions
-----------------------------------

There are several Jinja2 helpers available:

.. function:: label()

   Outputs the label associated with the field.

.. _Cross site request forgery: https://en.wikipedia.org/wiki/Cross-site_request_forgery
