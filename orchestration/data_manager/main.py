"""Module with an entrypoint for debugging purposes"""

from data_manager.jobs import LOCAL_CONFIG, build_datasets_job

if __name__ == "__main__":
    dev_config = dict(LOCAL_CONFIG)
    # Uncomment to limit the number of records
    # max_items = 1000
    # dev_config['ops'] = {
    #    'download_coches': {'config': {'max_items': max_items}},
    #    'download_motos': {'config': {'max_items': max_items}}
    # }
    build_datasets_job.execute_in_process(run_config=dev_config)
