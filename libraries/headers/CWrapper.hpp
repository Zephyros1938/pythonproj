#ifdef __cplusplus
#define C_WRAPPER_BEGIN extern "C" {
#define C_WRAPPER_END }
#else
#define C_WRAPPER_BEGIN
#define C_WRAPPER_END
#endif

#define C_WRAPPER(func) \
    decltype(func)* c_##func = &func;
