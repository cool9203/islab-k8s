import logging

logger = logging.getLogger(__name__)

import kubernetes.client
from kubernetes.client.rest import ApiException
from kubernetes.client.api_client import ApiClient
from kubernetes import client, config, utils
import six


class _kubeapi():
    def __init__(self):
        try:
            config.load_incluster_config()
        except Exception as e:
            config.load_kube_config()
        self.v1 = client.CoreV1Api()
        self.api_client = ApiClient()
        logger.debug("kubeapi init finish")

    def get_worker(self, worker_name, node_name):
        all_worker = self.get_all_worker(worker_name)
        for pod_name, pod_spec in all_worker.items():
            if (node_name == pod_spec["node_name"]):
                return pod_spec["pod_ip"]
        raise Exception(f"not have '{worker_name}' on '{node_name}' node")

    def get_all_worker(self, worker_name):
        return self.get_all_pod(worker_name)

    def get_all_pod(self, target=""):
        data = dict()
        ret = self.v1.list_pod_for_all_namespaces(watch=False)
        for pod in ret.items:
            if (len(target) > 0):
                if (target in pod.metadata.name):
                    data[pod.metadata.name] = {"pod_ip":pod.status.pod_ip, "namespace":pod.metadata.namespace, "node_name":pod.spec.node_name, "status":pod.status.phase}
            else:
                data[pod.metadata.name] = {"pod_ip":pod.status.pod_ip, "namespace":pod.metadata.namespace, "node_name":pod.spec.node_name, "status":pod.status.phase}
        return data

    def get_all_svc(self, target=""):
        data = dict()
        ret = self.v1.list_service_for_all_namespaces(watch=False)
        for svc in ret.items:
            if (len(target) > 0):
                if (target in svc.metadata.name):
                    data[svc.spec.cluster_ip] = {"name":svc.metadata.name, "namespace":svc.metadata.namespace, "ports":svc.spec.ports}
            else:
                data[svc.spec.cluster_ip] = {"name":svc.metadata.name, "namespace":svc.metadata.namespace, "ports":svc.spec.ports}
        return data

    def get_all_node(self, target=""):
        data = dict()
        ret = self.v1.list_node()
        for node in ret.items:
            gpu = node.status.capacity.get("nvidia.com/gpu")
            cpu_capacity = node.status.capacity["cpu"]
            cpu_allocatable = node.status.allocatable["cpu"]
            mem_capacity = node.status.capacity["memory"]
            mem_allocatable = node.status.allocatable["memory"]
            if (len(target) > 0):
                if (target in svc.metadata.name):
                    data[node.metadata.name] = {"gpu":gpu, "cpu_capacity":cpu_capacity, "cpu_allocatable":cpu_allocatable, "mem_capacity":mem_capacity, "mem_allocatable":mem_allocatable}
            else:
                data[node.metadata.name] = {"gpu":gpu, "cpu_capacity":cpu_capacity, "cpu_allocatable":cpu_allocatable, "mem_capacity":mem_capacity, "mem_allocatable":mem_allocatable}
        return data

    def mount_gpu_to_pod(self, pod_name, gpu_num=1, namespace="default"):
        ret = self.v1.connect_get_namespaced_service_proxy_with_path("gpu-mounter-service", "kube-system", f"addgpu/namespace/{namespace}/pod/{pod_name}/gpu/{gpu_num}/isEntireMount/false")
        logger.debug(f"{ret}")
        if ("Success" in ret):
            return True
        return False

    def remove_gpu_to_pod(self, pod_name, gpu_uuid=None, namespace="default", **kwargs):
        if (gpu_uuid is None):
            gpu_uuid = self.get_pod_mount_gpu_uuid(pod_name)

        if (len(gpu_uuid) == 0):
            return True

        logger.debug("uuid:{gpu_uuid}")
        form_params = list()
        for uuid in gpu_uuid:
            form_params.append(("uuids", uuid))
        ret = self.__call_api(
            name="gpu-mounter-service",
            namespace="kube-system",
            path=f"removegpu/namespace/{namespace}/pod/{pod_name}/force/1",
            header={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
            form=form_params,
            path2=None)

        logger.debug(ret)

        if ("Success" in str(ret)):
            return True
        return False

    def __call_api_GET_example(self):
        ret = self.v1.connect_get_namespaced_service_proxy_with_path("your_service_name", "kube-system", f"service_rul")

    def __call_api_POST_example(self):
        """
        this example call api in curl:
            curl --location \
            --request POST 'http://{ip}:{port}/api/v1/namespaces/kube-system/services/{your_service_name}/proxy/{service_rul}' \
            --header 'Content-Type: application/x-www-form-urlencoded' \
            --data-urlencode '{params_key}={your_para}'
        """
        form_params = list()
        for your_para in list():
            form_params.append(("params_key", your_para))
        ret = self.__call_api(
            name="your_service_name",
            namespace="kube-system",
            path=f"service_rul",
            header={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
            form=form_params,
            path2=None)

    def __call_api(self, **kwargs):
        #this function reference kubernetes/client/api/core_v1_api.py implement connect_post_namespaced_service_proxy_with_path_with_http_info function on k8s github
        local_var_params = locals()

        all_params = [
            'name',
            'namespace',
            'path',
            'header',
            'method',
            'form',
            'path2'
        ]
        all_params.extend(
            [
                'async_req',
                '_return_http_data_only',
                '_preload_content',
                '_request_timeout'
            ]
        )

        for key, val in six.iteritems(local_var_params['kwargs']):
            if key not in all_params:
                raise ApiTypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method connect_post_namespaced_service_proxy" % key
                )
            local_var_params[key] = val
        del local_var_params['kwargs']
        # verify the required parameter 'name' is set
        if self.api_client.client_side_validation and ('name' not in local_var_params or  # noqa: E501
                                                        local_var_params['name'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `name` when calling `connect_post_namespaced_service_proxy_with_path`")  # noqa: E501
        # verify the required parameter 'namespace' is set
        if self.api_client.client_side_validation and ('namespace' not in local_var_params or  # noqa: E501
                                                        local_var_params['namespace'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `namespace` when calling `connect_post_namespaced_service_proxy_with_path`")  # noqa: E501
        # verify the required parameter 'path' is set
        if self.api_client.client_side_validation and ('path' not in local_var_params or  # noqa: E501
                                                        local_var_params['path'] is None):  # noqa: E501
            raise ApiValueError("Missing the required parameter `path` when calling `connect_post_namespaced_service_proxy_with_path`")  # noqa: E501

        collection_formats = {}

        path_params = {}
        if 'name' in local_var_params:
            path_params['name'] = local_var_params['name']  # noqa: E501
        if 'namespace' in local_var_params:
            path_params['namespace'] = local_var_params['namespace']  # noqa: E501
        if 'path' in local_var_params:
            path_params['path'] = local_var_params['path']  # noqa: E501

        query_params = []
        if 'path2' in local_var_params and local_var_params['path2'] is not None:  # noqa: E501
            query_params.append(('path', local_var_params['path2']))  # noqa: E501

        header_params = dict() if not "header" in local_var_params or local_var_params["header"] is None else local_var_params["header"]

        form_params = list() if not "form" in local_var_params or local_var_params["form"] is None else local_var_params["form"]

        local_var_files = {}

        body_params = dict() if not "body" in local_var_params or local_var_params["body"] is None else local_var_params["body"]
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.select_header_accept(
            ['*/*'])  # noqa: E501

        # Authentication setting
        auth_settings = ['BearerToken']  # noqa: E501

        return self.api_client.call_api(
            '/api/v1/namespaces/{namespace}/services/{name}/proxy/{path}', local_var_params["method"],
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            response_type='str',  # noqa: E501
            auth_settings=auth_settings,
            async_req=local_var_params.get('async_req'),
            _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
            _preload_content=local_var_params.get('_preload_content', True),
            _request_timeout=local_var_params.get('_request_timeout'),
            collection_formats=collection_formats)

    def _apply_pv_pvc(self, pod_name):
        utils.create_from_yaml(self.api_client, f"./data/yaml/{pod_name}/pv.yaml")
        utils.create_from_yaml(self.api_client, f"./data/yaml/{pod_name}/pvc.yaml")

    def _apply_pod(self, pod_name):
        utils.create_from_yaml(self.api_client, f"./data/yaml/{pod_name}/pod.yaml")

    def _apply_svc(self, pod_name):
        utils.create_from_yaml(self.api_client, f"./data/yaml/{pod_name}/svc.yaml")

    def _apply(self, file_path):
        utils.create_from_yaml(self.api_client, file_path)

    def _delete_pod(self, name, namespace="default"):
        try:
            self.v1.delete_namespaced_pod(name, namespace)
            return True
        except Exception as e:
            return False

    def _delete_svc(self, name, namespace="default"):
        try:
            self.v1.delete_namespaced_service(name, namespace)
            return True
        except Exception as e:
            return False
