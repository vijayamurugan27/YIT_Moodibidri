import click
import json
from flask.cli import with_appcontext

@click.command()
@with_appcontext
def test_api():
    """Test API endpoints."""
    from flask import current_app
    
    with current_app.test_client() as client:
        try:
            # Create
            response = client.post('/api/students', json={'name': 'Test User', 'course': 'AI'})
            assert response.status_code == 201
            student_id = json.loads(response.data)['id']
            click.echo('✅ POST works')

            # Read
            response = client.get(f'/api/students/{student_id}')
            assert response.status_code == 200
            click.echo('✅ GET works')

            # Update
            response = client.put(f'/api/students/{student_id}', json={'course': 'ML'})
            assert response.status_code == 200
            click.echo('✅ PUT works')

            # Delete
            response = client.delete(f'/api/students/{student_id}')
            assert response.status_code == 200
            click.echo('✅ DELETE works')

            # Verify deletion
            response = client.get(f'/api/students/{student_id}')
            assert response.status_code == 404
            click.echo('✅ Delete verified')

            click.echo('🎉 All API tests passed!')
        
        except AssertionError as e:
            click.echo(f'❌ API test failed: {str(e)}')
        except Exception as e:
            click.echo(f'❌ Unexpected error: {str(e)}')
