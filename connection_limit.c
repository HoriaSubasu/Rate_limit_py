#include <stdio.h>
#include "httpd.h"
#include "http_core.h"
#include "http_protocol.h"
#include "http_request.h"
#include <hiredis/hiredis.h>

/* Define Global Variables */
static int active_connections = 0;
static const int max_nr_connections = 5;
char* client_ip;
redisContext *c;
redisReply *reply;


/* Define prototypes of our functions in this module */
static void register_hooks(apr_pool_t *pool);
static int connection_handler(request_rec *r);


/* Function converting string to integer */
int convert(char* str) {
    int num = 0;
    for (int i = 0; str[i] != '\0'; i++) {
        if (str[i] >= 48 && str[i] <= 57) {
            num = num * 10 + (str[i] - 48);
        }
        else {
            break;
        }
    }
    return num;
}
/* Define our module as an entity and assign a function for registering hooks  */
module AP_MODULE_DECLARE_DATA   connection_limit_module =
{
    STANDARD20_MODULE_STUFF,
    NULL,
    NULL,
    NULL,
    NULL,
    NULL,
    register_hooks   /* Our hook registering function */
};

/* register_hooks: Adds a hook to the httpd process */
static void register_hooks(apr_pool_t *pool)
{

    /* Hook the request handler */
    ap_hook_handler(connection_handler, NULL, NULL, APR_HOOK_LAST);
}
static int connection_handler(request_rec *r)
{
    /* First off, we need to check if this is a call for the "example" handler.
     * If it is, we accept it and do our things, it not, we simply return DECLINED,
     * and Apache will try somewhere else.
     */
    if (!r->handler || strcmp(r->handler, "connection_limit_module")) return (DECLINED);

    /* Connect to Redis DataBase */
    c = redisConnect("127.0.0.1", 6381);


    /* Check Redis connection */
    if (c->err) return HTTP_INTERNAL_SERVER_ERROR;



    client_ip = r->useragent_ip;
    reply = redisCommand(c, "GET %s", client_ip);
     /* Check to see if the connection contor was set for the IP */
    if (reply == NULL)
        reply = redisCommand(c, "SET key:%s %s", client_ip, 1);
        a = 5;
    else {
        reply = convert(reply);
        if (reply > max_nr_connections) {
                ap_set_content_type(r, "text/html");
                ap_rprintf(r, "Connection limit reached.\n");
                return HTTP_SERVICE_UNAVAILABLE;
        }
        else {
                reply = redisCommand(c, "INCR %s", client_ip);
                ap_rprintf(r, "Connection accepted.\n");
                return OK;
        }
    }

   // Simulate connection processing
    sleep(5); // Replace with real processing logic

    active_connections--;
    return OK;

    // The first thing we will do is write a simple "Hello, world!" back to the client.
    ap_rputs("Hello, world!<br/>", r);
    return OK;
}
