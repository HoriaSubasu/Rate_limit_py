from datetime import datetime
import redis
import subprocess

r = redis.Redis(host='localhost', port=6379, db=0)
RATE_LIMIT = 2
OFFENCES_ALLOWED = 5

def application(environ, start_response):
        client_ip = environ.get("REMOTE_ADDR", "0.0.0.0")
        block_key = "blocked:{}".format(client_ip)
        time_request = datetime.now().second    #The time at which the request was made in seconds


        if r.exists(block_key):         #The you are blocked case
                status = '503 Forbidden'
                output = b'Your IP has been permanently blocked due to too many requests.'
                response_headers = [('Content-type', 'text/plain'),
                                    ('Content-Length', str(len(output)))]
                start_response(status, response_headers)
                return [output]

        if r.get("{} timeout".format(client_ip)) == "Tru":      #The you are in timeout case
                time_now = datetime.now().minute
                if time_now - int(r.get("{} timeout applied at".format(client_ip))) != 0:
                        r.set("{} timeout".format(client_ip), "Fals")
                        subprocess.run(['iptables', '-D', 'INPUT', '-s', client_ip, '-j', 'DROP'])
                        status = '200 OK'
                        output = b'Hello, World'
                        response_headers = [('Content-type', 'text/plain'),('Content-Length', str(len(output)))]
                        start_response(status, response_headers)
                        return [output]
                else:
                        status = '403 Forbidden'
                        output = b'Your IP has been temporarily blocked due to too many requests.'
                        response_headers = [('Content-type', 'text/plain'),('Content-Length', str(len(output)))]
                        start_response(status, response_headers)
                        return [output]
        if r.exists(client_ip) == 0:            #The initialization phase
                r.set(client_ip, 1)             #The client IP addr is the name for the contor value of the request per second
                r.set("{} time of last request".format(client_ip), time_request)                #Setting the time in seconds for the request
                r.set("{} nr. of offences".format(client_ip), 0)        #Setting the number of offences at the server as 0.
                r.set("{} timeout".format(client_ip), "Fals")   #Setting the timeout status.
                r.set("{} timeout applied at".format(client_ip), 0)     #Setting the time that the timeout was applied
                status = '200 OK'
                output = b'Hello, World!'
                response_headers = [('Content-type', 'text/plain'),('Content-Length', str(len(output)))]
                start_response(status, response_headers)
                return [output]
        else:
                if time_request - int(r.get("{} time of last request".format(client_ip))) == 0:
                        r.incr(client_ip)
                        r.set("{} time of last request".format(client_ip), time_request)
                        nr_requests_per_second = int(r.get(client_ip))
                        if nr_requests_per_second > RATE_LIMIT:
                                r.incr("{} nr. of offences".format(client_ip))
                                nr_offences = int(r.get("{} nr. of offences".format(client_ip)))
                                if nr_offences > OFFENCES_ALLOWED:
                                        r.set(block_key, "Tru")
                                        subprocess.run(['iptables', '-A', 'INPUT', '-s', client_ip, '-j', 'DROP'])
                                        status = '503 Forbidden'
                                        output = b'Your IP has been blocked due to too many requests.'
                                        response_headers = [('Content-type', 'text/plain'),
                                                            ('Content-Length', str(len(output)))]
                                        start_response(status, response_headers)
                                        return [output]
                                else:
                                        r.incr("{} nr. of offences".format(client_ip))
                                        r.set("{} timeout".format(client_ip), "Tru")
                                        subprocess.run(['iptables', '-A', 'INPUT', '-s', client_ip, '-j', 'DROP'])
                                        r.set("{} timeout applied at".format(client_ip), datetime.now().minute)
                                        status = '403 Forbidden'
                                        output = b'Your IP has been temporarily blocked due to too many requests.'
                                        response_headers = [('Content-type', 'text/plain'),('Content-Length', str(len(output)))]
                                        start_response(status, response_headers)
                                        return [output]
				else:
                                        r.incr("{} nr. of offences".format(client_ip))
                                        r.set("{} timeout".format(client_ip), "Tru")
                                        subprocess.run(['iptables', '-A', 'INPUT', '-s', client_ip, '-j', 'DROP'])
                                        r.set("{} timeout applied at".format(client_ip), datetime.now().minute)
                                        status = '403 Forbidden'
                                        output = b'Your IP has been temporarily blocked due to too many requests.'
                                        response_headers = [('Content-type', 'text/plain'),('Content-Length', str(len(output)))]
                                        start_response(status, response_headers)
                                        return [output]
                        else:
                                        r.incr(client_ip)
                                        status = '200 OK'
                                        output = b'Hello, World!'
                                        response_headers = [('Content-type', 'text/plain'),('Content-Length', str(len(output)))]
                                        start_response(status, response_headers)
                                        return [output]
                else:
                        r.set(client_ip, 1)
                        r.set("{} time of last request".format(client_ip), time_request)
                        status = '200 OK'
                        output = b'Hello, World!'
                        response_headers = [('Content-type', 'text/plain'),('Content-Length', str(len(output)))]
                        start_response(status, response_headers)
                        return [output]


