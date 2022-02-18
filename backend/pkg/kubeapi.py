import kubernetes.client
from kubernetes.client.rest import ApiException
from kubernetes import client, config
import six

import logging

logger = logging.getLogger("master.kubeapi")


class __kubeapi():
    def __init__(self):
        config.load_incluster_config()
        self.v1 = client.CoreV1Api()
        logger.debug("kubeapi init finish")

    def get_all_worker(self, worker_name):
        all_pod_data = self.get_all_pod()
        all_worker = dict()
        for pod_name, data in all_pod_data.items():
            if (worker_name in pod_name):
                all_worker[pod_name] = data
        return all_worker

    def get_all_pod(self):
        data = dict()
        ret = self.v1.list_pod_for_all_namespaces(watch=False)
        for pod in ret.items:
            data[pod.metadata.name] = {"pod_ip":pod.status.pod_ip, "namespace":pod.metadata.namespace}
        return data

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
