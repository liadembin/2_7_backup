#
# def handle_register(args: str):
#     print("Requested to register: ")
#     username, password = args.split("~")
#     sessid, errors = sign_up_to_db(username, password)
#     print("Sign Up returned: ")
#     print(f"{sessid =}")
#     print(f"{errors =}")
#     if len(errors) > 0:
#         flattned = []
#         for code, msg in errors:
#             flattned.append(str(code))
#             flattned.append(msg)
#         return "REER~", "~".join(flattned)
#
#     return f"REGR~{sessid}", True
#
#
# def handle_signin(args: str):
#     username, password = args.split("~")
#     print(f"Sigin with: {username = } {password =}")
#     sessid, errors = sign_in_to_db(username, password)
#     print("Sign Up returned: ")
#     print(f"{sessid =}")
#     print(f"{errors =}")
#     if len(errors) > 0:
#         flattned = []
#         for code, msg in errors:
#             flattned.append(str(code))
#             flattned.append(msg)
#         return "REER~", "~".join(flattned)
#     print("Client Sessid: ", sessid)
#     return f"REGR~{sessid}", True
#
#
# def handle_get_inbox(args: str):
#     sessid = args
#     print("User with sessid requested: ", sessid)
#     user = get_user_by_sessid(sessid)
#     if user is None:
#         return "INBE~Invalid Session Token~1001", True
#     inbox = get_received_messages_by_id(user)[0]
#     encoded = to_base64_and_pickled(inbox)
#     return "BOXR~" + encoded, True
#
#
# def handle_get_outbox(args: str):
#     sessid = args
#     user = get_user_by_sessid(sessid)
#     if user is None:
#         return "OUTE~Invalid Session Token~1001", True
#     inbox = get_sent_messages_by_id(user)[0]
#     encoded = to_base64_and_pickled(inbox)
#     return "OUTR~" + encoded, True
#
#
# def handle_get_unread(args):
#     messages = get_unread_messages_from_sessid(args.split("~")[0])
#     # Add rsa encoding
#     encoded = to_base64_and_pickled(messages)
#     return "UNRR~" + encoded, True
#


def handle_add_message(args):
    sessid, msg = args.split("~")
    # succsess, error = add_message(sessid, msg)
    succsess, error = "", ""
    if error:
        return "ADME~" + error
    return "ADMR~" + succsess


def handle_get_public_key(args, thread):
    return "KEYR~" + thread.rsa_clien.public_key.n + "~" + thread.rsa_clien.public_key.e


def handle_get_enc_key(args, thread):
    pass
