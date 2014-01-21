.. _key_concepts_mvc:

MVC
===

Model View Controller (MVC) is a design pattern that encourages you to write code that adheres to seperation of concerns and DRY principles. It's also begun to be widely adapted into just about every single web framework available.

While Watson follows your standard mvc design pattern, it does not force you to use any particular ORM as your way to interact with models. It is up to you, the developer, to determine the most appropriate database abstraction method.

Terminology
-----------

Throughout the documentation various controllers, models and views will be referenced many times and it is important that they are interpreted within the context of the framework.

1. **Model**: The application data
2. **View**: The interface the user is presented with
3. **Controller**: Interprets a request and converts it to the relevant output

The basic lifecycle of a request
--------------------------------

What Watson does have an opinion on is lifecycle that a request must go through to become a response.

1. Browser request comes in
    A standard http request which is processed by server

2. Application run method executed
    This begins the processing of the request by Watson

3. Environ variables converted into watson.http.message.Request object
    This request object is considered immutable and should not be modified

4. Request matched against application routes
    Defined within your applications configuration file

5. Controller initialized
    A new controller is initialized on each request

6. Controller dispatch method executed returning a particular view
    The method called is based on the Request params, or the Request method depending on the controller type

7. Controller response converted to a watson.http.message.Response
    Used by the application to deliver the response

8. Response delivered to browser
    The relevant markup is sent to the users browser
