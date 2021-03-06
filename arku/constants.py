default_queue_name = 'arku:queue'
job_key_prefix = 'arku:job:'
in_progress_key_prefix = 'arku:in-progress:'
result_key_prefix = 'arku:result:'
retry_key_prefix = 'arku:retry:'
abort_jobs_ss = 'arku:abort'
# age of items in the abort_key sorted set after which they're deleted
abort_job_max_age = 60
health_check_key_suffix = ':health-check'
# how long to keep the "in_progress" key after a cron job ends to prevent the job duplication
# this can be a long time since each cron job has an ID that is unique for the intended execution time
keep_cronjob_progress = 60
