#pragma once

#include "net/http_client.h"
#include "misc_log_ex.h"
#include "cryptonote_core/cryptonote_core.h"
#include "cryptonote_protocol/cryptonote_protocol_handler.h"
#include "p2p/net_node.h"

namespace daemonize {

class t_rpc_command_executor final {
private:
  epee::net_utils::http::http_simple_client m_http_client;
  uint32_t m_ip;
  uint16_t m_port;
public:
  t_rpc_command_executor(
      uint32_t ip
    , uint16_t port
    );

  bool print_peer_list();

  bool save_blockchain();

  bool show_hash_rate();

  bool hide_hash_rate();

  bool show_difficulty();

  bool print_connections();

  bool print_blockchain_info(uint64_t start_block_index, uint64_t end_block_index);

  bool set_log_level(int8_t level);
  
  bool print_height();

  bool print_block_by_hash(crypto::hash block_hash);

  bool print_block_by_height(uint64_t height);

  bool print_transaction(crypto::hash transaction_hash);

  bool print_transaction_pool_long();

  bool print_transaction_pool_short();

  bool start_mining(cryptonote::account_public_address address, uint64_t num_threads);

  bool stop_mining();

  bool stop_daemon();

  bool print_status();

private:
  template <typename T_req, typename T_res>
  bool json_rpc_request(
      T_req & req
    , T_res & res
    , std::string const & method_name
    , std::string const & fail_msg
    );

  template <typename T_req, typename T_res>
  bool rpc_request(
      T_req & req
    , T_res & res
    , std::string const & relative_url
    , std::string const & fail_msg
    );
};

} // namespace daemonize
