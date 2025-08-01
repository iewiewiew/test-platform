import apiClient from "../../utils/request";

/**
 * 通用工具集 API 服务
 */
export const toolService = {
  // ==================== 编码/解码工具 ====================
  
  /**
   * URL编码
   */
  urlEncode(text) {
    return apiClient.post("/tools/url/encode", { text });
  },
  
  /**
   * URL解码
   */
  urlDecode(text) {
    return apiClient.post("/tools/url/decode", { text });
  },
  
  /**
   * Base64编码
   */
  base64Encode(text) {
    return apiClient.post("/tools/base64/encode", { text });
  },
  
  /**
   * Base64解码
   */
  base64Decode(text) {
    return apiClient.post("/tools/base64/decode", { text });
  },
  
  /**
   * JWT Token解析
   */
  jwtDecode(token, secret = null, verify = true) {
    return apiClient.post("/tools/jwt/decode", { token, secret, verify });
  },
  
  // ==================== 格式转换工具 ====================
  
  /**
   * JSON格式化
   */
  jsonFormat(jsonText, indent = 2) {
    return apiClient.post("/tools/json/format", { json: jsonText, indent });
  },
  
  /**
   * JSON压缩
   */
  jsonCompact(jsonText) {
    return apiClient.post("/tools/json/compact", { json: jsonText });
  },
  
  /**
   * XML转JSON
   */
  xmlToJson(xmlText) {
    return apiClient.post("/tools/xml/to-json", { xml: xmlText });
  },
  
  /**
   * 时间戳转日期时间
   */
  timestampToDatetime(timestamp, format = "%Y-%m-%d %H:%M:%S") {
    return apiClient.post("/tools/timestamp/to-datetime", { timestamp, format });
  },
  
  /**
   * 日期时间转时间戳
   */
  datetimeToTimestamp(datetime, format = "%Y-%m-%d %H:%M:%S") {
    return apiClient.post("/tools/datetime/to-timestamp", { datetime, format });
  },
  
  // ==================== 加密/解密工具 ====================
  
  /**
   * MD5哈希
   */
  md5Hash(text) {
    return apiClient.post("/tools/hash/md5", { text });
  },
  
  /**
   * SHA1哈希
   */
  sha1Hash(text) {
    return apiClient.post("/tools/hash/sha1", { text });
  },
  
  /**
   * SHA256哈希
   */
  sha256Hash(text) {
    return apiClient.post("/tools/hash/sha256", { text });
  },
  
  /**
   * SHA512哈希
   */
  sha512Hash(text) {
    return apiClient.post("/tools/hash/sha512", { text });
  },
  
  /**
   * HMAC哈希
   */
  hmacHash(text, key, algorithm = "sha256") {
    return apiClient.post("/tools/hash/hmac", { text, key, algorithm });
  },
  
  /**
   * AES加密
   */
  aesEncrypt(text, key, mode = "CBC") {
    return apiClient.post("/tools/aes/encrypt", { text, key, mode });
  },
  
  /**
   * AES解密
   */
  aesDecrypt(text, key, mode = "CBC") {
    return apiClient.post("/tools/aes/decrypt", { text, key, mode });
  },
  
  /**
   * RSA加密
   */
  rsaEncrypt(text, publicKey) {
    return apiClient.post("/tools/rsa/encrypt", { text, public_key: publicKey });
  },
  
  /**
   * RSA解密
   */
  rsaDecrypt(text, privateKey) {
    return apiClient.post("/tools/rsa/decrypt", { text, private_key: privateKey });
  },
  
  // ==================== 文本处理工具 ====================
  
  /**
   * 正则表达式测试
   */
  regexTest(text, pattern, flags = 0) {
    return apiClient.post("/tools/regex/test", { text, pattern, flags });
  },
  
  /**
   * 文本对比
   */
  textCompare(text1, text2, ignoreCase = false, ignoreWhitespace = false) {
    return apiClient.post("/tools/text/compare", { text1, text2, ignore_case: ignoreCase, ignore_whitespace: ignoreWhitespace });
  },
};

export default toolService;

