from django.db import models
from apps.enrollments.models import Enrollment
from apps.courses.models import Lesson

class Progress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='progresses')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')
        verbose_name_plural = 'Progresses'

    def __str__(self):
        return f"{self.enrollment.student.username} - {self.lesson.title} - {'Completed' if self.completed else 'Pending'}"
