import * as API from "./api";
import "lightbox2";

class Racine {
    constructor(apiToken) {
        this.apiClient = new API.ApiClient(window.location.origin);
        this.apiClient.authentications["bearerAuth"].accessToken = apiToken;

        this.samplesApi = new API.SamplesApi(this.apiClient);
        this.sharesAPI = new API.SharesApi(this.apiClient);
        this.actionsAPI = new API.ActionsApi(this.apiClient);
    }
}

export default Racine;