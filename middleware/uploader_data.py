import oss2
import os
import uuid
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from drf_spectacular.utils import extend_schema, OpenApiParameter
from .utils import ApiResponse

# 直接在代码中填写AccessKey和Endpoint
access_key_id = "LTAI5t9kmUmB7C8cRCes5si8"
access_key_secret = "mD4Ou2icxyoulhyzviDOfLqBsppACC"
endpoint = "oss-cn-beijing.aliyuncs.com"  # 例如oss-cn-hangzhou.aliyuncs.com
bucket_name = "flashcircle"

# 初始化OSS客户端
auth = oss2.Auth(access_key_id, access_key_secret)
bucket = oss2.Bucket(auth, endpoint, bucket_name)


@extend_schema(tags=['上传管理'])
class UploadResourceView(APIView):
    """
    上传资源接口
    接收文件和名称，返回访问地址
    """
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        summary='上传头像/图片/视频资源',
        description='上传文件到阿里云OSS，返回可访问的URL地址',
        parameters=[
            OpenApiParameter(
                name='type',
                type=str,
                location=OpenApiParameter.QUERY,
                description='文件类型: img, video 等',
                required=False
            ),
            OpenApiParameter(
                name='name',
                type=str,
                location=OpenApiParameter.QUERY,
                description='自定义文件名',
                required=False
            )
        ],
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': '要上传的文件'
                    }
                },
                'required': ['file']
            }
        },
        responses={
            200: {
                'description': '上传成功',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 200},
                                'message': {'type': 'string', 'example': '上传成功'},
                                'data': {
                                    'type': 'object',
                                    'properties': {
                                        'url': {'type': 'string', 'example': 'https://flashcircle.oss-cn-beijing.aliyuncs.com/video/video_01.mp4'},
                                        'name': {'type': 'string', 'example': 'video/video_01.mp4'}
                                    }
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': '请求参数错误',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 400},
                                'message': {'type': 'string', 'example': '未找到上传文件'},
                                'data': {'type': 'object', 'example': {}}
                            }
                        }
                    }
                }
            },
            500: {
                'description': '服务器内部错误',
                'content': {
                    'application/json': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'code': {'type': 'integer', 'example': 500},
                                'message': {'type': 'string', 'example': '上传过程中发生错误'},
                                'data': {'type': 'object', 'example': {}}
                            }
                        }
                    }
                }
            }
        }
    )
    def post(self, request):
        try:
            # 获取上传的文件
            uploaded_file = request.FILES.get('file')
            if not uploaded_file:
                return ApiResponse(
                    data={},
                    message="未找到上传文件",
                    code=400
                )

            # 获取type参数
            file_type = request.query_params.get('type', '')

            # 获取name参数（优先使用查询参数中的name，其次使用表单中的name，最后使用文件名）
            file_name = (request.query_params.get('name') or
                        request.POST.get('name') or
                        uploaded_file.name)

            # 如果没有提供文件名，则使用UUID生成唯一文件名
            if not file_name or file_name == uploaded_file.name:
                ext = os.path.splitext(uploaded_file.name)[1]
                file_name = f"{uuid.uuid4().hex}{ext}"

            # 构建带路径的文件名
            if file_type:
                full_file_name = f"{file_type}/{file_name}"
            else:
                full_file_name = file_name

            # 上传到OSS
            result = bucket.put_object(full_file_name, uploaded_file)

            if result.status == 200:
                # 生成文件访问URL
                file_url = f"https://{bucket_name}.{endpoint}/{full_file_name}"
                return ApiResponse(
                    data={
                        'url': file_url,
                        'name': full_file_name
                    },
                    message="上传成功",
                    code=200
                )
            else:
                return ApiResponse(
                    data={},
                    message=f"上传失败，状态码: {result.status}",
                    code=500
                )

        except oss2.exceptions.SignatureDoesNotMatch as e:
            return ApiResponse(
                data={},
                message="签名错误：AccessKey ID 或 AccessKey Secret 不正确",
                code=403
            )
        except oss2.exceptions.AccessDenied as e:
            return ApiResponse(
                data={},
                message="访问被拒绝：AccessKey 没有操作该 Bucket 的权限",
                code=403
            )
        except Exception as e:
            return ApiResponse(
                data={},
                message=f"上传过程中发生错误: {str(e)}",
                code=500
            )
