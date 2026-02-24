# Generated manually for monorepo preview tokens and metadata.
import secrets
from django.db import migrations, models
import zane_api.models.main


def populate_project_preview_tokens_and_service_slugs(apps, schema_editor):
    Project = apps.get_model("zane_api", "Project")
    PreviewEnvMetadata = apps.get_model("zane_api", "PreviewEnvMetadata")

    existing_tokens = set(
        Project.objects.exclude(preview_deploy_token__isnull=True).values_list(
            "preview_deploy_token", flat=True
        )
    )

    prefix = "pt_"
    for project in Project.objects.filter(preview_deploy_token__isnull=True):
        token = f"{prefix}{secrets.token_hex(16)}"
        while token in existing_tokens:
            token = f"{prefix}{secrets.token_hex(16)}"
        project.preview_deploy_token = token
        project.save(update_fields=["preview_deploy_token"])
        existing_tokens.add(token)

    for preview_meta in PreviewEnvMetadata.objects.select_related("service").all():
        if preview_meta.service is not None and len(preview_meta.updated_service_slugs) == 0:
            preview_meta.updated_service_slugs = [preview_meta.service.slug]
            preview_meta.save(update_fields=["updated_service_slugs"])


class Migration(migrations.Migration):

    dependencies = [
        ("zane_api", "0318_previewenvtemplate_stacks_to_clone"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="preview_deploy_token",
            field=models.CharField(max_length=64, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="previewenvmetadata",
            name="updated_service_slugs",
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.RunPython(
            populate_project_preview_tokens_and_service_slugs,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name="project",
            name="preview_deploy_token",
            field=models.CharField(
                default=zane_api.models.main.generate_project_preview_deploy_token,
                max_length=64,
                unique=True,
            ),
        ),
    ]
