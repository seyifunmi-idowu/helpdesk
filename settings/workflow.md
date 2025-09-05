{
  "events": {
    "ticket": {
      "select": {
        "ticket.created": "Ticket is Created",
        "ticket.updated": "Ticket is Updated",
        "ticket.agent.reply": "Agent Replied on Ticket",
        "ticket.customer.reply": "Customer Replied on Ticket",
        "ticket.note.added": "Note is Added on Ticket",
        "ticket.assign.agent": "Ticket is Assigned to Agent",
        "ticket.assign.group": "Ticket is Assigned to Group",
        "ticket.collaborator.added": "Collaborator is Added to Ticket",
        "ticket.priority.updated": "Ticket Priority is Updated",
        "ticket.status.updated": "Ticket Status is Updated",
        "ticket.type.updated": "Ticket Type is Updated",
        "ticket.deleted": "Ticket is Deleted"
      },
      "conditions": {
        "from_mail": "From Email",
        "to_mail": "To Email",
        "subject": "Subject",
        "description": "Description",
        "subject_or_description": "Subject or Description",
        "TicketPriority": "Priority",
        "TicketType": "Type",
        "TicketStatus": "Status",
        "source": "Source",
        "created": "Created Date",
        "agent": "Assigned Agent",
        "group": "Assigned Group",
        "team": "Assigned Team",
        "customer_name": "Customer Name",
        "customer_email": "Customer Email",
        "customFields": "Custom Fields"
      },
      "actions": {
        "uvdesk.ticket.add_note": {
          "label": "Add Note",
          "options": {
            "note": {
              "type": "textarea",
              "label": "Note"
            }
          }
        },
        "uvdesk.ticket.mail_agent": {
          "label": "Mail to Agent",
          "options": {
            "select_agent": {
              "type": "select",
              "label": "Select Agent",
              "values": "fetched_from_database"
            },
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.mail_customer": {
          "label": "Mail to Customer",
          "options": {
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.mail_group": {
          "label": "Mail to Group",
          "options": {
            "select_group": {
              "type": "select",
              "label": "Select Group",
              "values": "fetched_from_database"
            },
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.mail_last_collaborator": {
          "label": "Mail to Last Collaborator",
          "options": {
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.mail_team": {
          "label": "Mail to Team",
          "options": {
            "select_team": {
              "type": "select",
              "label": "Select Team",
              "values": "fetched_from_database"
            },
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.mark_spam": {
          "label": "Mark as Spam",
          "options": {}
        },
        "uvdesk.ticket.assign_agent": {
          "label": "Assign to Agent (Round Robin)",
          "options": {
            "select_agents": {
              "type": "multiselect",
              "label": "Select Agents",
              "values": "fetched_from_database"
            },
            "select_groups": {
              "type": "multiselect",
              "label": "Select Groups",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.update_agent": {
          "label": "Update Agent",
          "options": {
            "select_agent": {
              "type": "select",
              "label": "Select Agent",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.update_group": {
          "label": "Update Group",
          "options": {
            "select_group": {
              "type": "select",
              "label": "Select Group",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.update_label": {
          "label": "Update Label",
          "options": {
            "select_label": {
              "type": "select",
              "label": "Select Label",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.update_priority": {
          "label": "Update Priority",
          "options": {
            "select_priority": {
              "type": "select",
              "label": "Select Priority",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.update_status": {
          "label": "Update Status",
          "options": {
            "select_status": {
              "type": "select",
              "label": "Select Status",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.update_tag": {
          "label": "Update Tag",
          "options": {
            "tags": {
              "type": "text",
              "label": "Tags"
            }
          }
        },
        "uvdesk.ticket.update_team": {
          "label": "Update Team",
          "options": {
            "select_team": {
              "type": "select",
              "label": "Select Team",
              "values": "fetched_from_database"
            }
          }
        },
        "uvdesk.ticket.update_type": {
          "label": "Update Type",
          "options": {
            "select_type": {
              "type": "select",
              "label": "Select Type",
              "values": "fetched_from_database"
            }
          }
        }
      }
    },
    "customer": {
      "select": {
        "customer.created": "Customer is Created",
        "customer.updated": "Customer is Updated"
      },
      "conditions": {
        "customer_name": "Customer Name",
        "customer_email": "Customer Email"
      },
      "actions": {
        "uvdesk.customer.mail_customer": {
          "label": "Mail to Customer",
          "options": {
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        }
      }
    },
    "agent": {
      "select": {
        "agent.created": "Agent is Created"
      },
      "conditions": {
        "agent_name": "Agent Name"
      },
      "actions": {
        "uvdesk.agent.mail_agent": {
          "label": "Mail to Agent",
          "options": {
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        }
      }
    },
    "user": {
      "select": {
        "user.forgot_password": "User Forgot Password"
      },
      "conditions": {},
      "actions": {
        "uvdesk.user.mail_user": {
          "label": "Mail to User",
          "options": {
            "select_template": {
              "type": "select",
              "label": "Select Email Template",
              "values": "fetched_from_database"
            }
          }
        }
      }
    }
  }
}