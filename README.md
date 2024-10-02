# GSWA RDF Delta Consumer

This Azure Service Bus consumer consumes from a "sessionful" topic, processes the messages (RDF, RDF Patch Log or SPARQL Update queries) and sends it to either the RDF Delta Server or Fuseki SPARQL Update endpoint.

In a future iteration, it will integrate with Olis and do some message processing before sending it off to the target services.