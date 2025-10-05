def register_routes(app):
    """Register application routes"""
    
    @app.route('/')
    def index():
        return '''
        <h1>Flask Error Handling Demo</h1>
        <p>Test error pages:</p>
        <ul>
            <li><a href="/trigger-error/400">400 - Bad Request</a></li>
            <li><a href="/trigger-error/404">404 - Not Found</a></li>
            <li><a href="/trigger-error/500">500 - Server Error</a></li>
        </ul>
        <p>Test division:</p>
        <ul>
            <li><a href="/divide/10/2">10 ÷ 2 (Success)</a></li>
            <li><a href="/divide/10/0">10 ÷ 0 (Error)</a></li>
        </ul>
        '''
    
    # ... rest of your routes remain the same