from celery import shared_task

# from base.dj_clickhouse import get_clickhouse_client
#
#
# @shared_task(bind=True, max_retries=2, default_retry_delay=5, queue="shop_event")
# def task_track_event(self, user_id, product_id, event_type, ts):
#     try:
#         client = get_clickhouse_client()
#         client.insert(
#             "user_event",
#             [[user_id, product_id, event_type, ts]],
#             column_names=['user_id', 'product_id', 'event_type', 'created_at']
#         )
#     except Exception as e:
#         raise self.retry(exc=e)
