import R from '../racine';
import SwaggerUI from 'swagger-ui';

class SwaggerUIView {
  onDocumentReady() {
    const ui = SwaggerUI({
      dom_id: '#swagger-ui',
      url: '/static/api.yaml',
      onComplete: () => {
        ui.preauthorizeApiKey('bearerAuth', R.apiToken);
      }
    });
  }
}

export default SwaggerUIView;
