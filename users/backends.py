
# from django.contrib.auth.backends import ModelBackend
# from django.contrib.auth import get_user_model
# from ecp_lib.challenges import issue_authentication_challenge, verify_authentication_response
# from ecp_lib.auth import create_user_keys, create_challenge
 
# User = get_user_model()


# import logging
# logger = logging.getLogger("ecp")
# sec_logger = logging.getLogger("security")


# class ECPAuthBackend(ModelBackend):
#     def authenticate(self, request, username=None, password=None, key_file=None, **kwargs):
#         print(f"DEBUG BACKEND username={username} password={password} key_file={key_file}")
#         ip = request.META.get("REMOTE_ADDR") if request else None

#         logger.info(f"Login attempt | user={username} | ip={ip}")

#         if not username or not password or not key_file:
        
#             return None


#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             return None

#         if not user.check_password(password):
#             sec_logger.warning(f"Invalid credentials | user={username} | ip={ip}")
#             return None

#         logger.info(f"Password verified | user={username}")


#         try:
#             private_key_pem = key_file.read().decode("utf-8")
#             logger.debug(f"Private key file received | user={username}")

#             logger.info(f"Challenge issued | user={username}")

#             signature = sign_payload(private_key_pem, challenge_obj.challenge)
#             logger.debug(f"Challenge signed | user={username}")

#             verify_authentication_response(
#                 identifier=user.username,
#                 challenge=challenge_obj.challenge,
#                 signature=signature,
#                 public_key_pem=user.profile.public_key_pem,
#             )

#         except Exception:
#             logger.exception(f"ECP verification error | user={username}")
#             return None

#         logger.info(f"ECP authentication success | user={username} | ip={ip}")
#         return user