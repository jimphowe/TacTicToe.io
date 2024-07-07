To run game (locally):

1. Start redis `redis-server /opt/homebrew/etc/redis.conf`
2. Start timeout listener `python manage.py listen_for_timeouts`
3. Start server `python manage.py runserver`