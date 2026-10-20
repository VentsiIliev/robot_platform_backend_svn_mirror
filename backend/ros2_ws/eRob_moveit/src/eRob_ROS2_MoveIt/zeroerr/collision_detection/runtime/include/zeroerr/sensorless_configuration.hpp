#pragma once

#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <set>
#include <stdexcept>
#include <string>
#include <unistd.h>
#include <nlohmann/json.hpp>
#include <yaml-cpp/yaml.h>

namespace zeroerr
{
inline YAML::Node merge_sensorless(const YAML::Node & base, const YAML::Node & overlay)
{
  YAML::Node result = base && base.IsMap() ? YAML::Clone(base) : YAML::Node(YAML::NodeType::Map);
  for (const auto & entry : overlay) {
    const auto key = entry.first.as<std::string>();
    if (entry.second.IsMap() && result[key] && result[key].IsMap()) {
      result[key] = merge_sensorless(result[key], entry.second);
    } else {result[key] = YAML::Clone(entry.second);}
  }
  return result;
}

inline YAML::Node load_sensorless_layers(
  const std::filesystem::path & filename, std::set<std::string> stack = {})
{
  const auto path = std::filesystem::canonical(filename);
  if (!stack.insert(path.string()).second) {throw std::runtime_error("Sensorless include cycle: " + path.string());}
  auto raw = YAML::LoadFile(path.string());
  if (!raw.IsMap()) {throw std::runtime_error("Sensorless configuration must be a mapping");}
  YAML::Node result(YAML::NodeType::Map);
  if (raw["RUNTIME_INCLUDES"]) {
    if (!raw["RUNTIME_INCLUDES"].IsSequence()) {throw std::runtime_error("RUNTIME_INCLUDES must be a list");}
    for (const auto & include : raw["RUNTIME_INCLUDES"]) {
      result = merge_sensorless(result, load_sensorless_layers(path.parent_path() / include.as<std::string>(), stack));
    }
    raw.remove("RUNTIME_INCLUDES");
  }
  return merge_sensorless(result, raw);
}

inline YAML::Node load_sensorless_config(const std::filesystem::path & path)
{
  auto data = load_sensorless_layers(path);
  if (!data["schema_version"] || data["schema_version"].as<int>() != 1) {
    throw std::runtime_error("Unsupported sensorless schema_version");
  }
  for (const auto * section : {"controller", "monitor", "runtime"}) {
    if (!data[section] || !data[section].IsMap()) {throw std::runtime_error(std::string("Missing sensorless section ") + section);}
  }
  return data;
}

inline nlohmann::json sensorless_json(const YAML::Node & node)
{
  if (!node || node.IsNull()) {return nullptr;}
  if (node.IsMap()) {
    auto result = nlohmann::json::object();
    for (const auto & entry : node) {result[entry.first.as<std::string>()] = sensorless_json(entry.second);}
    return result;
  }
  if (node.IsSequence()) {
    auto result = nlohmann::json::array();
    for (const auto & value : node) {result.push_back(sensorless_json(value));}
    return result;
  }
  const auto text = node.Scalar();
  if (node.Tag() == "!" || node.Tag() == "tag:yaml.org,2002:str") {return text;}
  auto value = nlohmann::json::parse(text, nullptr, false);
  return value.is_discarded() ? nlohmann::json(text) : value;
}

inline std::string sensorless_profile_path(const std::string & package)
{
  const char * requested = std::getenv("ZEROERR_ACTIVE_PROFILE");
  const auto profile = requested ? std::string(requested) :
    YAML::LoadFile(package + "/config/runtime.yaml")["ACTIVE_PROFILE"].as<std::string>();
  if (profile.empty() || profile.find('/') != std::string::npos ||
    profile.find('\\') != std::string::npos || profile.find("..") != std::string::npos)
  {throw std::runtime_error("Invalid active profile for sensorless configuration");}
  return package + "/config/" + profile + "/sensorless_collision.yaml";
}

inline void save_sensorless_monitor_patch(
  const std::filesystem::path & filename, const nlohmann::json & patch)
{
  // Persist only differences in this profile, leaving the shared defaults untouched.
  const auto path = std::filesystem::canonical(filename);
  auto raw = YAML::LoadFile(path.string());
  YAML::Node inherited(YAML::NodeType::Map);
  if (raw["RUNTIME_INCLUDES"]) {
    for (const auto & include : raw["RUNTIME_INCLUDES"]) {
      inherited = merge_sensorless(inherited, load_sensorless_layers(path.parent_path() / include.as<std::string>()));
    }
  }
  const auto baseline = sensorless_json(inherited["monitor"]);
  for (auto item = patch.begin(); item != patch.end(); ++item) {
    if (baseline.is_object() && baseline.contains(item.key()) && baseline.at(item.key()) == item.value()) {
      if (raw["monitor"]) {raw["monitor"].remove(item.key());}
    } else {
      raw["monitor"][item.key()] = YAML::Load(item.value().dump());
    }
  }
  if (raw["monitor"] && raw["monitor"].size() == 0) {raw.remove("monitor");}
  YAML::Emitter output;
  output << raw;
  if (!output.good()) {throw std::runtime_error("Cannot serialize sensorless configuration");}
  std::string temporary = path.string() + ".tmp-XXXXXX";
  const int descriptor = mkstemp(temporary.data());
  if (descriptor < 0) {throw std::runtime_error("Cannot create sensorless configuration temporary file");}
  close(descriptor);
  try {
    std::ofstream file(temporary);
    file << output.c_str() << '\n';
    file.close();
    if (file.fail()) {throw std::runtime_error("Cannot write sensorless configuration");}
    std::filesystem::permissions(temporary, std::filesystem::status(path).permissions());
    std::filesystem::rename(temporary, path);
  } catch (...) {
    std::filesystem::remove(temporary);
    throw;
  }
}
}  // namespace zeroerr
