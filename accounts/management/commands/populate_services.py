from django.core.management.base import BaseCommand
from accounts.models import StreamingService


class Command(BaseCommand):
    help = 'Populate database with popular streaming services'

    def handle(self, *args, **kwargs):
        services = [
            {'provider_id': 8, 'name': 'Netflix', 'logo_path': '/t2yyOv40HZeVlLjYsCsPHnWLk4W.jpg'},
            {'provider_id': 9, 'name': 'Amazon Prime Video', 'logo_path': '/emthp39XA2YScoYL1p0sdbAH2WA.jpg'},
            {'provider_id': 15, 'name': 'Hulu', 'logo_path': '/zxrVdFjIjLqkfnwyghnfywTn3Lh.jpg'},
            {'provider_id': 337, 'name': 'Disney Plus', 'logo_path': '/7rwgEs15tFwyR9NPQ5vpzxTj19Q.jpg'},
            {'provider_id': 1899, 'name': 'Max', 'logo_path': '/6Q3ZYUNA9Hsgj6iWnVsw2gR5V6z.jpg'},  # HBO Max is now Max
            {'provider_id': 531, 'name': 'Paramount Plus', 'logo_path': '/xbhHHa1YgtpwhC8lb1NQ3ACVcLd.jpg'},
            {'provider_id': 386, 'name': 'Peacock', 'logo_path': '/8VCV78prwd9QzZnEm0ReO6bERDa.jpg'},
            {'provider_id': 350, 'name': 'Apple TV Plus', 'logo_path': '/6uhKBfmtzFqOcLousHwZuzcrScK.jpg'},
        ]
        
        for service_data in services:
            service, created = StreamingService.objects.get_or_create(
                provider_id=service_data['provider_id'],
                defaults={
                    'name': service_data['name'],
                    'logo_path': service_data['logo_path']
                }
            )
            if created:
                self.stdout.write(f"Created: {service.name}")
            else:
                self.stdout.write(f"Already exists: {service.name}")
        
        self.stdout.write(self.style.SUCCESS('Successfully populated streaming services'))