const axios = require('axios');
const { URLSearchParams } = require('url');
const { matchedData } = require('express-validator');
const { handleError } = require('../../../middleware/utils');

class LotInfoAPI {
    /**
     * Initialize API client for Lot Information
     * @param {string} baseUrl - Base API URL (e.g., "http://utlwebprd1/OEEwebAPI")
     * @param {string} logId - System log ID
     * @param {string} enNumber - Equipment number
     * @param {string} token - API token (default: "OEE_WEB_API")
     */
    constructor(
        baseUrl = "http://utlwebprd1/OEEwebAPI",
        logId = "1231562",
        enNumber = "226383",
        token = "OEE_WEB_API"
    ) {
        this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
        this.logId = logId;
        this.enNumber = enNumber;
        this.token = token;
        this.timeout = 10000; // 10 seconds in milliseconds
    }

    /**
     * Construct the API URL with proper encoding
     * @param {string[]} lotIds - List of Lot IDs to query
     * @returns {string} Properly encoded API URL
     */
    _buildUrl(lotIds) {
        // Create busItem parameter structure
        const busItem = lotIds.map(lotId => ({ LotID: lotId }));

        // Build query parameters
        const params = new URLSearchParams({
            logID: this.logId,
            enNumber: this.enNumber,
            token: this.token,
            busItem: JSON.stringify(busItem)
        });

        return `${this.baseUrl}/DataForOEE/LotInfo/GetLotInfo?${params.toString()}`;
    }

    /**
     * Get lot information from API
     * @param {string[]} lotIds - List of Lot IDs to retrieve
     * @param {number} maxRetries - Number of retry attempts (default: 3)
     * @returns {Promise<Object|null>} JSON response data or null on failure
     */
    async getLotInfo(lotIds, maxRetries = 3) {
        const url = this._buildUrl(lotIds);

        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                const response = await axios.get(url, {
                    timeout: this.timeout,
                    headers: { Accept: 'application/json' }
                });

                // Validate response format
                const data = response.data;
                if (!Array.isArray(data)) {
                    throw new Error("Unexpected response format");
                }

                return data[0];
            } catch (error) {
                console.error(`API request failed (attempt ${attempt + 1}/${maxRetries}): ${error.message}`);
                if (attempt === maxRetries - 1) {
                    return null;
                }
            }
        }

        return null;
    }

    /**
     * Convenience method for single Lot ID queries
     * @param {string} lotId - Lot ID to query
     * @returns {Promise<Object|null>} JSON response data or null on failure
     */
    async getSingleLotInfo(lotId) {
        return this.getLotInfo([lotId]);
    }
}

// Example usage
// (async () => {
//     const api = new LotInfoAPI();
//     const lotInfo = await api.getSingleLotInfo("12345");
//     console.log(lotInfo);
// })();

/**
 * Get lot information from API
 * @param {Object} req - request object
 * @param {Object} res - response object
 */
const getLotInfo = async (req, res) => {
    try {
        req = matchedData(req);
        // console.log(req.id);
        const api = new LotInfoAPI();
        res.status(200).json(await api.getSingleLotInfo(req.id));
    } catch (error) {
        handleError(res, error);
    }
}

module.exports = { getLotInfo };