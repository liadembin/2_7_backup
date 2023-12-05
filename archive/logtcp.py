def logtcp(dir, byte_data):
    """
    log direction and all TCP byte array data
    return: void
    """
    logger.info(f'LOG:{"Sent  >>>" if dir == "sent" else "Recived  <<<"} {byte_data}')
