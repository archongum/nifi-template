import argparse
import nipyapi
nipyapi.config.nifi_config.host = 'http://localhost:8080/nifi-api'
nipyapi.config.registry_config.host = 'http://localhost:18080/nifi-registry-api'
#Queues can be large - increase timeout
nipyapi.config.short_max_wait = 3600

parser = argparse.ArgumentParser()
parser.add_argument('--pg_id', default=None)
parser.add_argument('--bucket_name', default=None)
parser.add_argument('--flow_name', default=None)
parser.add_argument('--target_version', default=None)
args = parser.parse_args()

pg_id=args.pg_id
bucket_name=args.bucket_name
flow_name=args.flow_name
target_version=args.target_version
if target_version == 'latest':
    target_version = None
else:
    target_version = int(target_version)

def update_flow_ver(pg_id, bucket_name, flow_name, target_version=None):
    bucket = nipyapi.versioning.get_registry_bucket(identifier=bucket_name, identifier_type='name')
    flow = nipyapi.versioning.get_flow_in_bucket(bucket_id=bucket.identifier, identifier=flow_name, identifier_type='name')
    pgs = nipyapi.canvas.list_all_process_groups(pg_id=pg_id)
    total = len(pgs)
    i = 0
    for pg in pgs:
        i += 1
        ver_info = pg.component.version_control_information
        if ver_info and ver_info.flow_id == flow.identifier:
            nipyapi.versioning.update_flow_ver(pg, target_version)
            print('--- [%s] updated, i=%d, total=%d' % (pg.component.name, i, total))
    print('Done.')
    return None


def purge_process_group_by_connections(pg_id):
    conns = nipyapi.canvas.list_all_connections(pg_id=pg_id, descendants=True)
    total = len(conns)
    i = 0
    for conn in conns:
        i += 1
        if conn.status.aggregate_snapshot.flow_files_queued > 0:
            nipyapi.canvas.purge_connection(conn.id)
            print('--- emptied, i=%d, total=%d' % (i, total))
    print('Done.')
    return None

            
def purge_process_group(pg_id):
    pg = nipyapi.canvas.get_process_group(identifier=pg_id, identifier_type='id')
    print('-- pg name=%s' % (pg.component.name))
    rs = nipyapi.canvas.purge_process_group(pg)
    return rs


if __name__ == '__main__':
    update_flow_ver(pg_id, bucket_name, flow_name, target_version)