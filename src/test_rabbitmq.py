#!/usr/bin/env python3
# coding: utf-8
import sys, os, re
import pika
import json
#import smartROS

if __name__ == '__main__':

    connection=None

    exchange_name='elk_exchange'
    queue_name=None
    try:
        credentials = pika.PlainCredentials('elk', 'elk')
        parameters = pika.ConnectionParameters(host='10.174.2.165', credentials=credentials)
        
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        #for case if no exchaneg yet present - declare it. The same name and type as in logstash config
        channel.exchange_declare(exchange=exchange_name, 
                                 exchange_type='topic',
                                 durable=True)

        result = channel.queue_declare( exclusive=True,   #Only allow access by the current connection
                                        auto_delete=True, #Delete after consumer cancels or disconnects
                                       )
        queue_name = result.method.queue

        channel.queue_bind ( exchange=exchange_name, 
                             queue=queue_name,
                             routing_key = "#" #accept all messages
                             )

        print(' [*] Waiting for logs. To exit press CTRL+C')

        def callback(ch, method, properties, body):
            print(" [x] Received event from <{}> with topic <{}>".format(method.exchange,method.routing_key))

            data=None
            try:
                #data = json.loads(body.decode('utf-8')) # logs
                data = json.loads(body) # logs
                if method.routing_key.startswith("logs.ip.ban"):
                    print("=====================================================================================")
                    print("  IP ban request received from host <{}>".format(data['host']['name']))
                    print("=====================================================================================")
                    print("  time : {}".format(data['time']))
                    print("  ban.ip = {}".format(data['ban']['ip']))
                    print("  ban.counter = {}".format(data['ban']['counter']))
                    print("  ban.reason = {}".format(data['ban']['reason']))
                    print("=====================================================================================\n")

            except Exception as inst:
                data=body
                print(" raw data : {}".format(body))
                print("Failed to parse message!")
                print("Error: {}".format(type(inst)))
                print("args : {}".format(inst.args))
                print("msg  : {}".format(str(inst)))



        channel.basic_consume(callback,
                              queue=queue_name,
                              no_ack=True)

        channel.start_consuming()

    except KeyboardInterrupt:
        print("Interrupting...")
    except Exception as inst:
        print("Failed to run application!")
        print("Error: {}".format(type(inst)))
        print("args : {}".format(inst.args))
        print("msg  : {}".format(str(inst)))
        os._exit(1) 

    finally:
        if connection:
            connection.close()