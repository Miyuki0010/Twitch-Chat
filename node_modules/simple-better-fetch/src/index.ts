import nodeFetch from "node-fetch";
// import {RequestInfo, RequestInit} from "@types/node-fetch"
const fetch = async (url: string, options: any = {}): Promise<any> => {
	const response = await nodeFetch(url, options);
	const contentType = response.headers.get("content-type");
	let responseData;
	if (contentType?.includes("application/json")) {
		responseData = await response.json();
	} else if (contentType?.includes("text/html")) {
		responseData = await response.text();
    }
    
	if (!response.ok || !responseData) {
		responseData = { message: responseData?.message || response.statusText, code: responseData?.code || responseData?.status || response.status };
	}

	return responseData;
};

export = fetch;
