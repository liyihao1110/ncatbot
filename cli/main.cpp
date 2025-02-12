#include <iostream>
#include <fstream>
#include <string>
#include <filesystem>
#include <cstdlib>
#include <cstring>
#include <vector>

namespace fs = std::filesystem;

std::string pythonVersion = "3.12.9";

std::string getUserInput(const std::vector<std::string>& validInputs, const std::string& prompt, const std::string& defaultValue = "") {
    std::string userInput;
    bool isValid = false;

    // 提示用户输入
    std::cout << prompt;
    std::cin >> userInput;

    // 检查输入是否匹配
    for (const auto& input : validInputs) {
        if (userInput == input) {
            isValid = true;
            break;
        }
    }

    if (isValid) {
        return userInput;
    } else {
        // 如果存在默认值且第一次输入无效，返回默认值
        if (!defaultValue.empty()) {
            return defaultValue;
        } else {
            // 提示用户重新输入
            while (true) {
                std::cout << "无效输入，请重新输入: ";
                std::cin >> userInput;

                isValid = false;
                for (const auto& input : validInputs) {
                    if (userInput == input) {
                        isValid = true;
                        break;
                    }
                }

                if (isValid) {
                    return userInput;
                }
            }
        }
    }
}

void createDirectory(const std::string& path) {
    if (fs::exists(path)) {
        std::cerr << "已存在 ncatbot 路径: " << path << std::endl;
        std::cerr << "请手动删除该目录后重试" << std::endl;
        exit(EXIT_FAILURE);
    }
    if (!fs::create_directory(path)) {
        std::cerr << "Failed to create directory: " << path << std::endl;
        std::cerr << "这是一个内部错误, 请联系管理员\n";
        exit(EXIT_FAILURE);
    }
}

void installPythonWindows(const std::string& installDir) {
    std::string pythonUrl = "https://www.python.org/ftp/python/" + pythonVersion + "/python-" + pythonVersion + "-amd64.exe";
    std::string pythonExePath = installDir + "/python_installer.exe";
    std::string pythonInstallPath = installDir + "/Python";

    // 创建目标目录
    fs::create_directories(installDir);

    // 下载安装包
    system(("powershell -Command \"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "
            "Invoke-WebRequest -Uri '" + pythonUrl + "' -OutFile '" + pythonExePath + "'\"").c_str());

    // 静默安装配置
    std::string installCmd = "\"" + pythonExePath + "\" /quiet InstallAllUsers=0 ";
    installCmd += "TargetDir=\"" + pythonInstallPath + "\" ";
    installCmd += "PrependPath=0 AssociateFiles=0 Shortcuts=0 Include_launcher=0";

    // 执行安装
    system(installCmd.c_str());

    // 清理安装包
    // fs::remove(pythonExePath);

    // 安装pip
    // std::string pythonExe = pythonInstallPath + "/python.exe";
    // system(("\"" + pythonExe + "\" -m ensurepip --upgrade --default-pip").c_str());
}

void installPythonLinux(const std::string& installDir) {
    std::string pythonTarUrl = "https://www.python.org/ftp/python/" + pythonVersion + "/Python-" + pythonVersion + ".tar.xz";
    std::string pythonTarPath = installDir + "/Python-" + pythonVersion + ".tar.xz";
    std::string pythonBuildPath = installDir + "/Python-" + pythonVersion;
    std::string pythonInstallPath = installDir + "/python";

    // 安装编译依赖
    system("sudo apt-get update > /dev/null 2>&1");
    system("sudo apt-get install -y --no-install-recommends build-essential zlib1g-dev libncurses5-dev "
           "libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev libbz2-dev > /dev/null 2>&1");

    // 下载源码
    system(("curl -sSL -o '" + pythonTarPath + "' '" + pythonTarUrl + "'").c_str());

    // 解压源码
    system(("tar -xf '" + pythonTarPath + "' -C '" + installDir + "'").c_str());

    // 配置编译选项
    std::string configureCmd = "cd '" + pythonBuildPath + "' && ";
    configureCmd += "./configure --prefix='" + pythonInstallPath + "' ";
    configureCmd += "--enable-optimizations --with-ensurepip=install --enable-loadable-sqlite-extensions > /dev/null 2>&1";

    // 编译安装
    system(configureCmd.c_str());
    system(("cd '" + pythonBuildPath + "' && make -j$(nproc) > /dev/null 2>&1 && make altinstall > /dev/null 2>&1").c_str());

    // 验证安装
    // std::string pythonExe = pythonInstallPath + "/bin/python3";
    // system(("\"" + pythonExe + "\" -m pip install --upgrade pip > /dev/null 2>&1"));

    // 清理临时文件
    fs::remove(pythonTarPath);
    fs::remove_all(pythonBuildPath);
}

void installPython(const std::string& installDir) {
    std::cout << "我们将在当前工作目录下安装独立的 Python 环境, 不会修改系统变量, 请确认:\n";
    std::string confirm = getUserInput({"y", "n"}, "是否安装 Python 环境? (y/n): ");
    if(confirm == "n") {
        std::cout << "已取消安装\n";
        exit(0);
    }
    #ifdef _WIN32
    installPythonWindows(installDir);
    #else
    installPythonLinux(installDir);
    #endif
}

int main(int argc, char* argv[]) {
    const std::string ncatbotDir = "ncatbot";
    const std::string pythonDir = ncatbotDir + "/python";

    // Create ncatbot directory
    createDirectory(ncatbotDir);

    // Install Python
    installPython(ncatbotDir);

    std::cout << "Python installed in " << pythonDir << std::endl;

    return 0;
}
