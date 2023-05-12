from rest_framework.routers import DefaultRouter

from .views import RecordViewset, OperationViewset

router = DefaultRouter()

router.register(r"record", RecordViewset, basename="record")
router.register(r"operation", OperationViewset, basename="operation")
urlpatterns = router.urls
