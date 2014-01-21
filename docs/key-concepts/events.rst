.. _key_concepts_events:

Events
======

Events are a major part of how Watson wires together your application. You can hook into the events and register your own event listeners by modifying your application configuration.

The event dispatcher holds a record of all listeners and the their associated priority, number of executions, and the event name that they are to be executed on.

.. note::
    The basic flow for the event system within Watson is the following:

    Create dispatcher > Add listeners > Trigger event > Return results from triggered listeners

The anatomy of an Event
-----------------------

An event is used to pass around data within an application without introducing a tight coupling between objects. A basic event contains the following:

A name
    The name of the event that will trigger listener callbacks
A target
    What triggered the event
A set of parameters
    Data sent through with the event

When an event is triggered from an event dispatcher, all listeners that are listening for a particular event name will be triggered and their responses returned.

Inbuilt events
--------------

The lifecycle of a Watson application is maintained by 5 different events defined in watson.framework.events:

event.framework.init
    Triggered when the application is started
event.framework.route.match
    Triggered when the application attempts to route a request and returns the matches
event.framework.dispatch.execute
    Triggered when the controller is executed and returns the response
event.framework.render.view
    Triggered when the controller response is processed and the view is rendered
event.framework.exception
    Triggered when any exception occurs within the application and the executes prior to the render view to generate any 400/500 error pages

These events are triggered by the shared_event_dispatcher which is instantiated from the applications IocContainer.

Creating and registering your own event listeners
-------------------------------------------------
By default several listeners are defined within the watson.framework.config module, however additional listeners can be added to these events, and even prevent the default listeners from being triggered.

Let's assume that we want to add a new listener to the watson.framework.events.INIT event. First lets add a new events key to the applications configuration module. Replace app_name with the applications name.

*app_name/config/config.py*

.. code-block:: python

    from watson.framework import events

    events = {
    }

.. note::
    Whatever defined in here will be **appended** to Watsons default configuration.

Next, we'll need to create a listener, which just needs to be a callable object. As the listener is going to be retrieved from the IocContainer, it is useful to subclass watson.di.ContainerAware so that the container will be injected automatically. The triggered listener is passed a single event as the argument, so make sure that you allow for that.

*app_name/listeners.py*

.. code-block:: python

    from watson.di import ContainerAware
    from watson.framework import listeners

    class MyFirstListener(listeners.Base, ContainerAware):
        def __call__(self, event):
            # we'll perform something based on the event and target here
            pass

Finally we'll need to register the listener with the event dispatcher. Each listener needs to be added as a tuple, which takes the following arguments: (object, int priority, boolean once_only). If no priority is specified a default priority of 1 will be given. The highest priority will be executed first. If only_once is not specified then it will default to False.

*app_name/config/config.py*

.. code-block:: python

    events = {
        events.INIT: [
            ('app_name.listeners.MyFirstListener', 2, True)
        ]
    }

Now once your application is initialized your event will be triggered.
